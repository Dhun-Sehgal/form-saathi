"""Import every model so SQLAlchemy / Alembic see the full schema."""
from .admin import Announcement, CorrectionReport, Feedback, SourceVerificationLog
from .ai import ChatMessage, ChatSession, EligibilityCheck
from .documents import UploadedDocument
from .engagement import (
    Application, ApplicationNote, ApplicationStatusHistory, Collection, Reminder, SavedOpportunity,
)
from .notifications import Notification, NotificationPreference
from .resume import RESUME_TEMPLATES, Resume
from .opportunity import (
    Category, DocumentType, EligibilityCriterion, Opportunity, OpportunityDate, Organization,
    RequiredDocument, opportunity_education_levels, opportunity_states,
)
from .user import RevokedToken, State, User, UserProfile, UserToken, profile_interest_categories

__all__ = [
    "Announcement", "Application", "ApplicationNote", "ApplicationStatusHistory", "Category",
    "ChatMessage", "ChatSession", "Collection", "CorrectionReport", "DocumentType",
    "EligibilityCheck", "EligibilityCriterion", "Feedback", "Notification",
    "NotificationPreference", "Opportunity", "OpportunityDate", "Organization", "Reminder",
    "RequiredDocument", "Resume", "RESUME_TEMPLATES", "RevokedToken", "SavedOpportunity", "SourceVerificationLog", "State",
    "UploadedDocument", "User", "UserProfile", "UserToken", "opportunity_education_levels",
    "opportunity_states", "profile_interest_categories",
]
