"""Central models registry exporting Declarative Base and all 29 domain entities."""

from src.models.admin import AdminPermission, AuditLog
from src.models.applications import ApplicationReview, VolunteerApplication
from src.models.attendance import AttendanceCorrection, AttendanceRecord
from src.models.base import Base
from src.models.communications import CommunicationJob, CommunicationLog
from src.models.consent import ConsentHistory, ConsentRecord
from src.models.events import Event, EventRegistration, RegistrationHistory
from src.models.gamification import (
    AchievementDefinition,
    PointTransaction,
    VolunteerAchievement,
)
from src.models.media import EventPhoto, MediaAsset
from src.models.notifications import DeviceToken, Notification
from src.models.rate_limit import RateLimitAttempt
from src.models.reports import ReportExport
from src.models.users import EmailVerification, PasswordResetToken, User, UserSession
from src.models.volunteers import (
    AlumniProfile,
    CorporateProfile,
    StudentProfile,
    VolunteerProfile,
)

__all__ = [
    "Base",
    # Module 1
    "User",
    "UserSession",
    "EmailVerification",
    "PasswordResetToken",
    "RateLimitAttempt",
    # Module 2
    "VolunteerProfile",
    "StudentProfile",
    "AlumniProfile",
    "CorporateProfile",
    # Module 3
    "VolunteerApplication",
    "ApplicationReview",
    # Module 4
    "ConsentRecord",
    "ConsentHistory",
    # Module 5
    "Event",
    "EventRegistration",
    "RegistrationHistory",
    # Module 6
    "AttendanceRecord",
    "AttendanceCorrection",
    # Module 7
    "PointTransaction",
    "AchievementDefinition",
    "VolunteerAchievement",
    # Module 8
    "Notification",
    "DeviceToken",
    # Module 9
    "CommunicationJob",
    "CommunicationLog",
    # Module 10
    "MediaAsset",
    "EventPhoto",
    # Module 11
    "AdminPermission",
    "AuditLog",
    # Module 12
    "ReportExport",
]
