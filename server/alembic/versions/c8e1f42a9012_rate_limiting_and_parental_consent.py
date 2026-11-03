"""Add rate_limit_attempts table, email_verifications attempt counters, volunteer_profiles consent flags, and expand users status check.

Revision ID: c8e1f42a9012
Revises: 97bb517503d6
Create Date: 2026-11-02 22:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "c8e1f42a9012"
down_revision = "97bb517503d6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Create rate_limit_attempts table
    op.create_table(
        "rate_limit_attempts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("identifier", sa.String(length=255), nullable=False),
        sa.Column("endpoint_key", sa.String(length=100), nullable=False),
        sa.Column("window_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("attempt_count", sa.Integer(), nullable=False, server_default="1"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("identifier", "endpoint_key", name="uq_rate_limit_identifier_endpoint"),
    )
    op.create_index(
        "ix_rate_limit_attempts_identifier_endpoint",
        "rate_limit_attempts",
        ["identifier", "endpoint_key"],
        unique=False,
    )
    op.create_index(
        "ix_rate_limit_attempts_window_start",
        "rate_limit_attempts",
        ["window_start"],
        unique=False,
    )

    # 2. Add attempt counters to email_verifications
    op.add_column(
        "email_verifications",
        sa.Column("attempt_count", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "email_verifications",
        sa.Column("max_attempts", sa.Integer(), nullable=False, server_default="5"),
    )

    # 3. Add explicit parental consent tri-state columns to volunteer_profiles
    op.add_column(
        "volunteer_profiles",
        sa.Column(
            "parental_consent_claimed",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )
    op.add_column(
        "volunteer_profiles",
        sa.Column(
            "parental_consent_evidence_submitted",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )
    op.add_column(
        "volunteer_profiles",
        sa.Column(
            "parental_consent_verified",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )

    # 4. Update check constraint on users.status to support PENDING_VERIFICATION, PENDING_APPROVAL, INACTIVE
    op.drop_constraint("chk_users_status", "users", type_="check")
    op.create_check_constraint(
        "chk_users_status",
        "users",
        "status IN ('PENDING_VERIFICATION', 'PENDING_APPROVAL', 'APPROVED', 'REJECTED', 'SUSPENDED', 'INACTIVE', 'UNVERIFIED', 'PENDING')",
    )


def downgrade() -> None:
    op.drop_constraint("chk_users_status", "users", type_="check")
    op.create_check_constraint(
        "chk_users_status",
        "users",
        "status IN ('UNVERIFIED', 'PENDING', 'APPROVED', 'REJECTED', 'SUSPENDED')",
    )
    op.drop_column("volunteer_profiles", "parental_consent_verified")
    op.drop_column("volunteer_profiles", "parental_consent_evidence_submitted")
    op.drop_column("volunteer_profiles", "parental_consent_claimed")
    op.drop_column("email_verifications", "max_attempts")
    op.drop_column("email_verifications", "attempt_count")
    op.drop_index("ix_rate_limit_attempts_window_start", table_name="rate_limit_attempts")
    op.drop_index("ix_rate_limit_attempts_identifier_endpoint", table_name="rate_limit_attempts")
    op.drop_table("rate_limit_attempts")

