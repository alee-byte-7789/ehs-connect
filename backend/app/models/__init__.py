"""
Import every model here so that `Base.metadata` is fully populated in one
place. Alembic's env.py imports this package (not individual model files)
so `--autogenerate` always sees the complete schema.
"""
from app.models.house import House
from app.models.resident import Resident
from app.models.admin import Admin
from app.models.staff import Staff
from app.models.complaint import Complaint
from app.models.complaint_history import ComplaintHistory
from app.models.feedback import Feedback
from app.models.application_feedback import ApplicationFeedback
from app.models.emergency_contact import EmergencyContact
from app.models.notification import Notification
from app.models.refresh_token import RefreshToken

__all__ = [
    "House",
    "Resident",
    "Admin",
    "Staff",
    "Complaint",
    "ComplaintHistory",
    "Feedback",
    "ApplicationFeedback",
    "EmergencyContact",
    "Notification",
    "RefreshToken",
]
