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

    # Enable RLS on all tenant tables
    for table in ["organizations", "projects", "tasks", "comments", "attachments",
                  "notifications", "activity_logs", "sprints", "time_entries",
                  "webhooks", "api_keys", "audit_logs"]:
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")

    # Tenant isolation policies
    op.execute("""
        CREATE POLICY tenant_isolation ON projects
        USING (organization_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)
    """)
    op.execute("""
        CREATE POLICY tenant_isolation ON sprints
        USING (project_id IN (
            SELECT id FROM projects
            WHERE organization_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid
        ))
    """)

    # Full-text search materialized view
    op.execute("""
        CREATE MATERIALIZED VIEW IF NOT EXISTS task_search AS
        SELECT
            t.id, t.project_id, p.organization_id,
            t.task_number, t.title, t.status, t.priority, t.assignee_id,
            to_tsvector('english',
                t.title || ' ' || COALESCE(t.description, '')
            ) AS search_vector
        FROM tasks t
        JOIN projects p ON p.id = t.project_id
    """)
    op.execute("CREATE INDEX IF NOT EXISTS idx_task_search_fts ON task_search USING GIN(search_vector)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_task_search_org ON task_search(organization_id)")


def downgrade() -> None:
    op.execute("DROP MATERIALIZED VIEW IF EXISTS task_search")
    op.execute("DROP POLICY IF EXISTS tenant_isolation ON projects")
    op.execute("DROP POLICY IF EXISTS tenant_isolation ON sprints")
    for table in ["organizations", "projects", "tasks", "comments", "attachments",
                  "notifications", "activity_logs", "sprints", "time_entries",
                  "webhooks", "api_keys", "audit_logs"]:
        op.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY")
    op.drop_table("audit_logs")
    op.drop_table("webhook_deliveries")
