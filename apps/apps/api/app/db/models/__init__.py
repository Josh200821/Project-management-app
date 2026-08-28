"""Import every model so SQLAlchemy's declarative registry can resolve the
string-based relationship() targets used throughout (e.g. Task.comments ->
"Comment"). Without this, whichever relationship happens to be configured
first raises InvalidRequestError as soon as any query touches it, since only
whatever models the *current* entrypoint happened to import would be known to
the mapper.

Anything that imports app.db.models (this package) gets every model
registered as a side effect - see app/db/base.py, which every repository and
service already transitively imports.
"""

from app.db.models.activity_log import ActivityLog
from app.db.models.api_key import ApiKey
from app.db.models.attachment import Attachment
from app.db.models.audit_log import AuditLog
from app.db.models.comment import Comment
from app.db.models.notification import Notification
from app.db.models.organization import Organization
from app.db.models.organization_member import OrganizationMember
from app.db.models.project import Project
from app.db.models.sprint import Sprint
from app.db.models.task import Task
from app.db.models.time_entry import TimeEntry
from app.db.models.user import User
from app.db.models.webhook import Webhook

__all__ = [
    "ActivityLog",
    "ApiKey",
    "Attachment",
    "AuditLog",
    "Comment",
    "Notification",
    "Organization",
    "OrganizationMember",
    "Project",
    "Sprint",
    "Task",
    "TimeEntry",
    "User",
    "Webhook",
]
