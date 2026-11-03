"""Persistence and SQL aggregation abstractions for Admin Dashboard, Reports, and Audit Logs."""

import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Any

from sqlalchemy import and_, desc, distinct, func, or_, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.admin import AuditLog
from src.models.attendance import AttendanceRecord
from src.models.consent import ConsentRecord
from src.models.events import Event, EventRegistration
from src.models.gamification import PointTransaction
from src.models.reports import ReportExport
from src.models.users import User
from src.models.volunteers import (
    AlumniProfile,
    CorporateProfile,
    StudentProfile,
    VolunteerProfile,
)


def _to_utc(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


class ReportRepository:
    """Database persistence and SQL aggregation repository for Administrative Dashboards and Reports."""

    async def get_admin_dashboard_metrics(self, db: AsyncSession) -> dict[str, Any]:
        """Aggregate real database statistics for administrative dashboard using consolidated CTE query."""
        import json

        # Handle dialect-specific JSON aggregation functions (PostgreSQL vs SQLite for unit testing)
        bind = db.get_bind()
        is_sqlite = bind and "sqlite" in bind.dialect.name
        json_agg = "json_group_object" if is_sqlite else "json_object_agg"

        consolidated_sql = text(f"""
            SELECT
              (SELECT count(*) FROM volunteer_profiles) AS total_volunteers,
              (SELECT count(*) FROM users WHERE role = 'VOLUNTEER' AND status = 'APPROVED' AND is_active = true) AS active_volunteers,
              (SELECT {json_agg}(coalesce(category, 'OTHER'), count) FROM (
                  SELECT category, count(*) as count FROM volunteer_profiles GROUP BY category
              ) s) AS category_counts,
              (SELECT {json_agg}(coalesce(status, 'OTHER'), count) FROM (
                  SELECT status, count(*) as count FROM users WHERE role = 'VOLUNTEER' GROUP BY status
              ) s) AS app_status_counts,
              (SELECT count(*) FROM events) AS total_events,
              (SELECT {json_agg}(coalesce(status, 'OTHER'), count) FROM (
                  SELECT status, count(*) as count FROM events GROUP BY status
              ) s) AS event_status_counts,
              (SELECT count(*) FROM event_registrations) AS total_registrations,
              (SELECT coalesce(sum(hours_credited), 0.00) FROM point_transactions) AS total_hours,
              (SELECT coalesce(sum(total_points), 0.00) FROM point_transactions) AS total_points;
        """)

        metrics_res = await db.execute(consolidated_sql)
        row = metrics_res.mappings().one()

        def _parse_json_dict(val: Any) -> dict[str, Any]:
            if isinstance(val, str):
                try:
                    return json.loads(val)
                except Exception:
                    return {}
            return val or {}

        total_volunteers = int(row["total_volunteers"] or 0)
        active_volunteers = int(row["active_volunteers"] or 0)

        # 1. Category breakdown
        cat_counts = _parse_json_dict(row["category_counts"])
        by_category = {cat: int(cat_counts.get(cat, 0)) for cat in ("STUDENT", "ALUMNI", "CORPORATE")}
        for k, v in cat_counts.items():
            by_category[k] = int(v)

        # 2. Application status breakdown
        app_counts = _parse_json_dict(row["app_status_counts"])
        pending_apps = (
            int(app_counts.get("SUBMITTED", 0))
            + int(app_counts.get("UNDER_REVIEW", 0))
            + int(app_counts.get("UNVERIFIED", 0))
            + int(app_counts.get("PENDING", 0))
        )
        approved_apps = int(app_counts.get("APPROVED", 0))
        rejected_apps = int(app_counts.get("REJECTED", 0))
        total_apps = sum(int(v) for v in app_counts.values())

        # 3. Event stats
        total_events = int(row["total_events"] or 0)
        event_status_counts = _parse_json_dict(row["event_status_counts"])
        by_event_status = {k: int(v) for k, v in event_status_counts.items()}
        completed_events = by_event_status.get("COMPLETED", 0)

        # 4. Engagement
        total_registrations = int(row["total_registrations"] or 0)
        total_hours = f"{Decimal(str(row['total_hours'] or '0.00')):.2f}"
        total_points = f"{Decimal(str(row['total_points'] or '0.00')):.2f}"

        # 5. Recent Activity from Audit Logs (Query 2)
        activity_stmt = (
            select(AuditLog)
            .options(selectinload(AuditLog.actor))
            .order_by(AuditLog.created_at.desc())
            .limit(10)
        )
        activity_res = await db.execute(activity_stmt)
        recent_logs = list(activity_res.scalars().all())

        activity_items = [
            {
                "id": log.id,
                "action": log.action,
                "actor_email": log.actor.email if log.actor else None,
                "resource_type": log.resource_type,
                "resource_id": log.resource_id,
                "created_at": log.created_at,
            }
            for log in recent_logs
        ]

        return {
            "volunteers": {
                "total_volunteers": total_volunteers,
                "active_volunteers": active_volunteers,
                "by_category": by_category,
            },
            "applications": {
                "pending": pending_apps,
                "approved": approved_apps,
                "rejected": rejected_apps,
                "total": total_apps,
            },
            "events": {
                "total_events": total_events,
                "by_status": by_event_status,
                "completed_events": completed_events,
            },
            "engagement": {
                "total_registrations": total_registrations,
                "total_hours_credited": total_hours,
                "total_points_allocated": total_points,
            },
            "recent_activity": activity_items,
        }

    async def get_student_contributions(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> tuple[list[dict[str, Any]], int]:
        """Student Contribution Report aggregation."""
        # Count total students
        count_res = await db.execute(
            select(func.count(VolunteerProfile.id)).where(VolunteerProfile.category == "STUDENT")
        )
        total = count_res.scalar() or 0

        # Subquery for events attended, hours credited, points earned
        pt_filter = []
        if start_date:
            pt_filter.append(PointTransaction.created_at >= start_date)
        if end_date:
            pt_filter.append(PointTransaction.created_at <= end_date)

        stmt = (
            select(
                VolunteerProfile.id,
                VolunteerProfile.first_name,
                VolunteerProfile.last_name,
                StudentProfile.college_name,
                StudentProfile.department,
                StudentProfile.batch_year,
                StudentProfile.maatram_reg_number,
                func.coalesce(func.count(distinct(PointTransaction.event_id)), 0).label(
                    "events_attended"
                ),
                func.coalesce(func.sum(PointTransaction.hours_credited), Decimal("0.00")).label(
                    "hours_credited"
                ),
                func.coalesce(func.sum(PointTransaction.total_points), Decimal("0.00")).label(
                    "points_earned"
                ),
            )
            .outerjoin(StudentProfile, StudentProfile.volunteer_profile_id == VolunteerProfile.id)
            .outerjoin(
                PointTransaction,
                and_(
                    PointTransaction.volunteer_profile_id == VolunteerProfile.id,
                    *pt_filter,
                ),
            )
            .where(VolunteerProfile.category == "STUDENT")
            .group_by(
                VolunteerProfile.id,
                VolunteerProfile.first_name,
                VolunteerProfile.last_name,
                StudentProfile.college_name,
                StudentProfile.department,
                StudentProfile.batch_year,
                StudentProfile.maatram_reg_number,
            )
            .order_by(desc("points_earned"), VolunteerProfile.first_name.asc())
            .offset(skip)
            .limit(limit)
        )

        rows = (await db.execute(stmt)).all()
        items = [
            {
                "volunteer_id": r[0],
                "student_name": f"{r[1]} {r[2]}".strip(),
                "college_name": r[3] or "Unknown",
                "department": r[4] or "Unknown",
                "batch_year": r[5],
                "maatram_reg_number": r[6],
                "events_attended": r[7],
                "hours_credited": f"{r[8]:.2f}",
                "points_earned": f"{r[9]:.2f}",
            }
            for r in rows
        ]
        return items, total

    async def get_alumni_contributions(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> tuple[list[dict[str, Any]], int]:
        """Alumni Contribution Report aggregation."""
        count_res = await db.execute(
            select(func.count(VolunteerProfile.id)).where(VolunteerProfile.category == "ALUMNI")
        )
        total = count_res.scalar() or 0

        pt_filter = []
        if start_date:
            pt_filter.append(PointTransaction.created_at >= start_date)
        if end_date:
            pt_filter.append(PointTransaction.created_at <= end_date)

        stmt = (
            select(
                VolunteerProfile.id,
                VolunteerProfile.first_name,
                VolunteerProfile.last_name,
                AlumniProfile.graduation_year,
                AlumniProfile.organisation,
                AlumniProfile.job_role,
                func.coalesce(func.count(distinct(PointTransaction.event_id)), 0).label(
                    "events_attended"
                ),
                func.coalesce(func.sum(PointTransaction.hours_credited), Decimal("0.00")).label(
                    "hours_credited"
                ),
                func.coalesce(func.sum(PointTransaction.total_points), Decimal("0.00")).label(
                    "points_earned"
                ),
            )
            .outerjoin(AlumniProfile, AlumniProfile.volunteer_profile_id == VolunteerProfile.id)
            .outerjoin(
                PointTransaction,
                and_(
                    PointTransaction.volunteer_profile_id == VolunteerProfile.id,
                    *pt_filter,
                ),
            )
            .where(VolunteerProfile.category == "ALUMNI")
            .group_by(
                VolunteerProfile.id,
                VolunteerProfile.first_name,
                VolunteerProfile.last_name,
                AlumniProfile.graduation_year,
                AlumniProfile.organisation,
                AlumniProfile.job_role,
            )
            .order_by(desc("points_earned"), VolunteerProfile.first_name.asc())
            .offset(skip)
            .limit(limit)
        )

        rows = (await db.execute(stmt)).all()
        items = [
            {
                "volunteer_id": r[0],
                "alumni_name": f"{r[1]} {r[2]}".strip(),
                "graduation_batch": r[3],
                "employer": r[4],
                "designation": r[5],
                "events_attended": r[6],
                "hours_credited": f"{r[7]:.2f}",
                "points_earned": f"{r[8]:.2f}",
            }
            for r in rows
        ]
        return items, total

    async def get_alumni_consistency(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[dict[str, Any]], int]:
        """Alumni Participation Consistency across calendar years."""
        count_res = await db.execute(
            select(func.count(VolunteerProfile.id)).where(VolunteerProfile.category == "ALUMNI")
        )
        total = count_res.scalar() or 0

        # Query distinct alumni
        alumni_stmt = (
            select(
                VolunteerProfile.id,
                VolunteerProfile.first_name,
                VolunteerProfile.last_name,
                AlumniProfile.graduation_year,
                AlumniProfile.organisation,
            )
            .outerjoin(AlumniProfile, AlumniProfile.volunteer_profile_id == VolunteerProfile.id)
            .where(VolunteerProfile.category == "ALUMNI")
            .order_by(VolunteerProfile.first_name.asc())
            .offset(skip)
            .limit(limit)
        )
        alumni_rows = (await db.execute(alumni_stmt)).all()
        alumni_ids = [r[0] for r in alumni_rows]

        # Query yearly stats for these alumni
        yearly_map: dict[uuid.UUID, list[dict[str, Any]]] = {aid: [] for aid in alumni_ids}
        if alumni_ids:
            year_col = func.extract("year", PointTransaction.created_at).label("yr")
            yr_stmt = (
                select(
                    PointTransaction.volunteer_profile_id,
                    year_col,
                    func.count(distinct(PointTransaction.event_id)),
                    func.coalesce(func.sum(PointTransaction.hours_credited), Decimal("0.00")),
                )
                .where(PointTransaction.volunteer_profile_id.in_(alumni_ids))
                .group_by(PointTransaction.volunteer_profile_id, year_col)
                .order_by(year_col.asc())
            )
            yr_rows = (await db.execute(yr_stmt)).all()
            for vol_id, yr, ev_cnt, hrs in yr_rows:
                if vol_id in yearly_map and yr is not None:
                    yearly_map[vol_id].append(
                        {
                            "year": int(yr),
                            "events_attended": ev_cnt,
                            "hours_credited": f"{hrs:.2f}",
                        }
                    )

        items = []
        for r in alumni_rows:
            metrics = yearly_map.get(r[0], [])
            years_active = len(metrics)
            items.append(
                {
                    "volunteer_id": r[0],
                    "alumni_name": f"{r[1]} {r[2]}".strip(),
                    "graduation_batch": r[3],
                    "employer": r[4],
                    "yearly_metrics": metrics,
                    "years_active_count": years_active,
                    "is_consistent": years_active >= 2,
                }
            )
        return items, total

    async def get_inactive_volunteers(
        self,
        db: AsyncSession,
        threshold_days: int = 180,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[dict[str, Any]], int]:
        """Detect inactive volunteers with no attendance in the last N days."""
        now = datetime.now(UTC)
        cutoff_date = now - timedelta(days=threshold_days)

        # Max attendance check-out date per volunteer
        last_att_subq = (
            select(
                EventRegistration.volunteer_profile_id,
                func.max(AttendanceRecord.check_out_time).label("last_active"),
            )
            .join(
                AttendanceRecord,
                AttendanceRecord.event_registration_id == EventRegistration.id,
            )
            .where(AttendanceRecord.status == "COMPLETED")
            .group_by(EventRegistration.volunteer_profile_id)
            .subquery()
        )

        # Eligible volunteers: either never attended, or last active < cutoff_date
        stmt = (
            select(
                VolunteerProfile.id,
                VolunteerProfile.first_name,
                VolunteerProfile.last_name,
                User.email,
                VolunteerProfile.category,
                VolunteerProfile.created_at,
                last_att_subq.c.last_active,
            )
            .join(User, User.id == VolunteerProfile.user_id)
            .outerjoin(
                last_att_subq,
                last_att_subq.c.volunteer_profile_id == VolunteerProfile.id,
            )
            .where(
                User.status == "APPROVED",
                or_(
                    last_att_subq.c.last_active.is_(None),
                    last_att_subq.c.last_active < cutoff_date,
                ),
            )
            .order_by(
                last_att_subq.c.last_active.desc().nullslast(), VolunteerProfile.created_at.asc()
            )
        )

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await db.execute(count_stmt)).scalar() or 0

        rows = (await db.execute(stmt.offset(skip).limit(limit))).all()

        items = []
        for r in rows:
            last_dt: datetime | None = _to_utc(r[6])
            reg_dt: datetime = _to_utc(r[5]) or now
            if last_dt is not None:
                days_inactive = (now - last_dt).days
            else:
                days_inactive = (now - reg_dt).days

            items.append(
                {
                    "volunteer_id": r[0],
                    "name": f"{r[1]} {r[2]}".strip(),
                    "email": r[3],
                    "category": r[4],
                    "registration_date": reg_dt,
                    "last_activity_date": last_dt,
                    "days_inactive": max(0, days_inactive),
                }
            )

        return items, total

    async def get_interview_availability(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[dict[str, Any]], int]:
        """Interview Availability Report with strict contact availability masking."""
        stmt = (
            select(
                VolunteerProfile.id,
                VolunteerProfile.first_name,
                VolunteerProfile.last_name,
                VolunteerProfile.category,
                VolunteerProfile.mobile_number,
                User.email,
                ConsentRecord.contact_available,
                AlumniProfile.organisation.label("alumni_emp"),
                AlumniProfile.job_role.label("alumni_desig"),
                CorporateProfile.organisation.label("corp_emp"),
                CorporateProfile.designation.label("corp_desig"),
                CorporateProfile.skills.label("corp_sector"),
                CorporateProfile.years_of_experience.label("corp_exp"),
            )
            .join(User, User.id == VolunteerProfile.user_id)
            .outerjoin(
                ConsentRecord,
                ConsentRecord.volunteer_profile_id == VolunteerProfile.id,
            )
            .outerjoin(
                AlumniProfile,
                AlumniProfile.volunteer_profile_id == VolunteerProfile.id,
            )
            .outerjoin(
                CorporateProfile,
                CorporateProfile.volunteer_profile_id == VolunteerProfile.id,
            )
            .where(
                User.status == "APPROVED",
                VolunteerProfile.category.in_(["ALUMNI", "CORPORATE"]),
            )
            .order_by(VolunteerProfile.category.desc(), VolunteerProfile.first_name.asc())
        )

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await db.execute(count_stmt)).scalar() or 0

        rows = (await db.execute(stmt.offset(skip).limit(limit))).all()

        items = []
        for r in rows:
            is_contact_available = bool(r[6])
            employer = r[7] or r[9] or "N/A"
            designation = r[8] or r[10] or "N/A"
            skills_raw = r[11]
            if isinstance(skills_raw, list):
                skills = [str(s) for s in skills_raw]
            elif skills_raw:
                skills = [str(skills_raw)]
            else:
                skills = []

            exp_years = float(r[12]) if r[12] is not None else None

            raw_phone = r[4] or ""
            raw_email = r[5] or ""

            if is_contact_available:
                phone_display = raw_phone
                email_display = raw_email
                is_masked = False
            else:
                # Mask phone and email
                phone_display = "[MASKED]"
                email_display = "[MASKED]"
                is_masked = True

            items.append(
                {
                    "volunteer_id": r[0],
                    "name": f"{r[1]} {r[2]}".strip(),
                    "category": r[3],
                    "employer": employer,
                    "designation": designation,
                    "skills": skills,
                    "experience_years": exp_years,
                    "phone_number": phone_display,
                    "email": email_display,
                    "is_contact_masked": is_masked,
                }
            )

        return items, total

    async def get_organisation_contributions(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> tuple[list[dict[str, Any]], int]:
        """Grouped by employer/company name across Corporate and Alumni volunteers."""
        # Unify organisation name from CorporateProfile and AlumniProfile
        org_name_expr = func.coalesce(
            CorporateProfile.organisation,
            AlumniProfile.organisation,
            "Independent / Unknown",
        ).label("org_name")

        pt_filter = []
        if start_date:
            pt_filter.append(PointTransaction.created_at >= start_date)
        if end_date:
            pt_filter.append(PointTransaction.created_at <= end_date)

        stmt = (
            select(
                org_name_expr,
                func.count(distinct(VolunteerProfile.id)).label("vol_count"),
                func.coalesce(func.count(distinct(PointTransaction.event_id)), 0).label(
                    "events_count"
                ),
                func.coalesce(func.sum(PointTransaction.hours_credited), Decimal("0.00")).label(
                    "hours_sum"
                ),
                func.coalesce(func.sum(PointTransaction.total_points), Decimal("0.00")).label(
                    "points_sum"
                ),
            )
            .select_from(VolunteerProfile)
            .outerjoin(
                CorporateProfile, CorporateProfile.volunteer_profile_id == VolunteerProfile.id
            )
            .outerjoin(AlumniProfile, AlumniProfile.volunteer_profile_id == VolunteerProfile.id)
            .outerjoin(
                PointTransaction,
                and_(
                    PointTransaction.volunteer_profile_id == VolunteerProfile.id,
                    *pt_filter,
                ),
            )
            .where(VolunteerProfile.category.in_(["CORPORATE", "ALUMNI"]))
            .group_by(org_name_expr)
            .order_by(desc("hours_sum"), desc("vol_count"))
        )

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await db.execute(count_stmt)).scalar() or 0

        rows = (await db.execute(stmt.offset(skip).limit(limit))).all()
        items = [
            {
                "organisation_name": r[0],
                "volunteer_count": r[1],
                "total_events_attended": r[2],
                "total_hours_credited": f"{r[3]:.2f}",
                "total_points_earned": f"{r[4]:.2f}",
            }
            for r in rows
        ]
        return items, total

    async def create_report_export(
        self,
        db: AsyncSession,
        requested_by_user_id: uuid.UUID,
        report_type: str,
        parameters: dict[str, Any],
        expires_at: datetime,
    ) -> ReportExport:
        """Create a report export tracking record."""
        exp = ReportExport(
            requested_by_user_id=requested_by_user_id,
            report_type=report_type,
            parameters=parameters,
            status="PENDING",
            expires_at=expires_at,
            created_at=datetime.now(UTC),
        )
        db.add(exp)
        await db.flush()
        await db.refresh(exp)
        return exp

    async def get_report_export_by_id(
        self, db: AsyncSession, export_id: uuid.UUID
    ) -> ReportExport | None:
        """Fetch report export by ID."""
        stmt = select(ReportExport).where(ReportExport.id == export_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_audit_logs(
        self,
        db: AsyncSession,
        actor_id: uuid.UUID | None = None,
        action: str | None = None,
        resource_type: str | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[AuditLog], int]:
        """Query system audit trail with filters and pagination."""
        stmt = select(AuditLog).options(selectinload(AuditLog.actor))
        count_stmt = select(func.count()).select_from(AuditLog)

        if actor_id:
            stmt = stmt.where(AuditLog.actor_user_id == actor_id)
            count_stmt = count_stmt.where(AuditLog.actor_user_id == actor_id)
        if action:
            stmt = stmt.where(AuditLog.action == action)
            count_stmt = count_stmt.where(AuditLog.action == action)
        if resource_type:
            stmt = stmt.where(AuditLog.resource_type == resource_type)
            count_stmt = count_stmt.where(AuditLog.resource_type == resource_type)
        if from_date:
            stmt = stmt.where(AuditLog.created_at >= from_date)
            count_stmt = count_stmt.where(AuditLog.created_at >= from_date)
        if to_date:
            stmt = stmt.where(AuditLog.created_at <= to_date)
            count_stmt = count_stmt.where(AuditLog.created_at <= to_date)

        stmt = stmt.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit)

        total_res = await db.execute(count_stmt)
        total = total_res.scalar() or 0

        logs = list((await db.execute(stmt)).scalars().all())
        return logs, total


report_repository = ReportRepository()
