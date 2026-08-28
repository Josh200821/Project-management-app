"""Enterprise tables: webhooks, api_keys, audit_logs, time_entries, sprints RLS.

Revision ID: 002
Revises: 001
Create Date: 2026-01-01
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, ARRAY, INET, JSONB

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # NOTE: every table below was referenced later in this same migration (the
    # RLS-enabling loop, or webhook_deliveries' FK to webhooks) and by the ORM
    # models/services/routers, but none of them were ever actually created --
    # migration 001 only creates users/organizations/projects/sprints/tasks.
    # Running `alembic upgrade head` against a fresh database would have
    # failed the moment it hit `ALTER TABLE comments ENABLE ROW LEVEL
    # SECURITY` (or, once that's fixed, "webhooks" for webhook_deliveries'
    # foreign key) with a "relation does not exist" error.
    op.create_table(
        "organization_members",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("organization_id", UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role", sa.String(50), nullable=False, server_default="'member'"),
        sa.Column("accepted_at", sa.TIMESTAMP(timezone=True)),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("organization_id", "user_id", name="uq_org_member"),
    )
    op.create_index("idx_org_members_org", "organization_members", ["organization_id"])
    op.create_index("idx_org_members_user", "organization_members", ["user_id"])

    op.create_table(
        "comments",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("task_id", UUID(as_uuid=True), sa.ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False),
        sa.Column("author_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("edited_at", sa.TIMESTAMP(timezone=True)),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("idx_comments_task", "comments", ["task_id"])

    op.create_table(
        "attachments",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("task_id", UUID(as_uuid=True), sa.ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False),
        sa.Column("uploaded_by", UUID(as_uuid=True), sa.ForeignKey("users.id")),
        sa.Column("file_name", sa.String(500), nullable=False),
        sa.Column("storage_key", sa.String(1000), nullable=False),
        sa.Column("content_type", sa.String(255)),
        sa.Column("size_bytes", sa.BigInteger()),
        sa.Column("av_clean", sa.Boolean()),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("idx_attachments_task", "attachments", ["task_id"])

    op.create_table(
        "notifications",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("organization_id", UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("type", sa.String(100), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("body", sa.Text()),
        sa.Column("entity_type", sa.String(100)),
        sa.Column("entity_id", UUID(as_uuid=True)),
        sa.Column("read_at", sa.TIMESTAMP(timezone=True)),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("idx_notifications_user", "notifications", ["user_id", sa.text("created_at DESC")])

    op.create_table(
        "activity_logs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("organization_id", UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("actor_id", UUID(as_uuid=True), sa.ForeignKey("users.id")),
        sa.Column("action", sa.String(255), nullable=False),
        sa.Column("entity_type", sa.String(100)),
        sa.Column("entity_id", UUID(as_uuid=True)),
        sa.Column("metadata", JSONB),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("idx_activity_logs_org", "activity_logs", ["organization_id", sa.text("created_at DESC")])

    op.create_table(
        "time_entries",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("task_id", UUID(as_uuid=True), sa.ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("started_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("stopped_at", sa.TIMESTAMP(timezone=True)),
        sa.Column("duration_seconds", sa.Integer()),
        sa.Column("description", sa.Text()),
        sa.Column("billable", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("idx_time_entries_task", "time_entries", ["task_id"])

    op.create_table(
        "webhooks",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("organization_id", UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("events", ARRAY(sa.String()), nullable=False),
        sa.Column("secret", sa.String(255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("failure_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_success_at", sa.TIMESTAMP(timezone=True)),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("idx_webhooks_org", "webhooks", ["organization_id"])

    op.create_table(
        "api_keys",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("organization_id", UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("key_hash", sa.String(255), nullable=False, unique=True),
        sa.Column("key_prefix", sa.String(20), nullable=False),
        sa.Column("last_used_at", sa.TIMESTAMP(timezone=True)),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("idx_api_keys_user", "api_keys", ["user_id"])

    op.create_table(
        "webhook_deliveries",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("webhook_id", UUID(as_uuid=True), sa.ForeignKey("webhooks.id", ondelete="CASCADE"), nullable=False),
        sa.Column("event_type", sa.String(100), nullable=False),
        sa.Column("payload", JSONB, nullable=False),
        sa.Column("response_status", sa.Integer),
        sa.Column("response_body", sa.Text),
        sa.Column("attempt_count", sa.Integer, nullable=False, server_default="1"),
        sa.Column("delivered_at", sa.TIMESTAMP(timezone=True)),
        sa.Column("next_retry_at", sa.TIMESTAMP(timezone=True)),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    # Audit logs — immutable, no update/delete
    op.create_table(
        "audit_logs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("organization_id", UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("actor_id", UUID(as_uuid=True)),
        sa.Column("actor_email", sa.String(255)),
        sa.Column("ip_address", INET),
        sa.Column("user_agent", sa.Text),
        sa.Column("action", sa.String(255), nullable=False),
        sa.Column("resource_type", sa.String(100)),
        sa.Column("resource_id", UUID(as_uuid=True)),
        sa.Column("outcome", sa.String(20)),
        sa.Column("metadata", JSONB),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("idx_audit_org", "audit_logs", ["organization_id", sa.text("created_at DESC")])

    # Revoke delete/update on audit_logs from app user
    op.execute("DO $$ BEGIN IF EXISTS (SELECT FROM pg_roles WHERE rolname='app_user') THEN REVOKE UPDATE, DELETE ON audit_logs FROM app_user; END IF; END $$;")

    # Enable RLS on all tenant tables. `projects` and `sprints` already got
    # their tenant_isolation policy in migration 001 -- re-creating it here
    # (as the original version of this migration did) would fail with
    # "policy already exists". organizations/tasks are RLS-enabled in 001 too
    # (ENABLE ROW LEVEL SECURITY is idempotent, so re-running it here is
    # harmless); the rest are new tables created just above.
    for table in ["organizations", "projects", "tasks", "comments", "attachments",
                  "notifications", "activity_logs", "sprints", "time_entries",
                  "webhooks", "api_keys", "audit_logs", "organization_members"]:
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")


def downgrade() -> None:
    # task_search + its indexes are owned by migration 001 (this migration's
    # copies were IF NOT EXISTS no-ops against what 001 already created), so
    # nothing to drop here for them.
    op.drop_table("webhook_deliveries")
    op.drop_table("audit_logs")
    # Dropping each table also drops the RLS policies/enablement created on
    # it above -- no separate DISABLE ROW LEVEL SECURITY / DROP POLICY needed.
    for table in ["api_keys", "webhooks", "time_entries", "activity_logs",
                  "notifications", "attachments", "comments", "organization_members"]:
        op.drop_table(table)
