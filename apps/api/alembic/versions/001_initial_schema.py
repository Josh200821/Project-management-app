"""001 initial schema — core tables, RLS, indexes.

Revision ID: 001
Revises: 
Create Date: 2026-01-01
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Extensions
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    op.execute("CREATE EXTENSION IF NOT EXISTS btree_gin")

    op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("password_hash", sa.Text()),
        sa.Column("full_name", sa.String(255)),
        sa.Column("avatar_url", sa.Text()),
        sa.Column("mfa_secret", sa.Text()),
        sa.Column("mfa_enabled", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("last_login_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "organizations",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False, unique=True),
        sa.Column("logo_url", sa.Text()),
        sa.Column("plan", sa.String(50), nullable=False, server_default="'free'"),
        sa.Column("stripe_customer_id", sa.String(255)),
        sa.Column("stripe_subscription_id", sa.String(255)),
        sa.Column("max_seats", sa.Integer(), nullable=False, server_default="5"),
        sa.Column("storage_bytes_used", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "projects",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("organization_id", UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("status", sa.String(50), nullable=False, server_default="'active'"),
        sa.Column("task_counter", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_by", UUID(as_uuid=True), sa.ForeignKey("users.id")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.UniqueConstraint("organization_id", "slug"),
    )

    op.create_table(
        "sprints",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("project_id", UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("goal", sa.Text()),
        sa.Column("start_date", sa.Date()),
        sa.Column("end_date", sa.Date()),
        sa.Column("status", sa.String(50), nullable=False, server_default="'planning'"),
        sa.Column("capacity_points", sa.Integer()),
        sa.Column("velocity_points", sa.Integer()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "tasks",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("project_id", UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("parent_task_id", UUID(as_uuid=True), sa.ForeignKey("tasks.id", ondelete="SET NULL")),
        sa.Column("sprint_id", UUID(as_uuid=True), sa.ForeignKey("sprints.id", ondelete="SET NULL")),
        sa.Column("task_number", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("status", sa.String(50), nullable=False, server_default="'todo'"),
        sa.Column("priority", sa.String(50), nullable=False, server_default="'medium'"),
        sa.Column("story_points", sa.Integer()),
        sa.Column("due_date", sa.DateTime(timezone=True)),
        sa.Column("assignee_id", UUID(as_uuid=True), sa.ForeignKey("users.id")),
        sa.Column("created_by", UUID(as_uuid=True), sa.ForeignKey("users.id")),
        sa.Column("board_order", sa.Float(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.UniqueConstraint("project_id", "task_number"),
    )

    # Indexes
    op.create_index("idx_projects_org", "projects", ["organization_id"])
    op.create_index("idx_tasks_board", "tasks", ["project_id", "status", "board_order"])
    op.execute(
        "CREATE INDEX idx_tasks_fts ON tasks USING GIN "
        "(to_tsvector('english', title || ' ' || coalesce(description,'')))"
    )
    op.execute("CREATE INDEX idx_tasks_trgm ON tasks USING GIN (title gin_trgm_ops)")

    # RLS
    for table in ["organizations", "projects", "tasks", "sprints"]:
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        op.execute(
            f"CREATE POLICY tenant_isolation ON {table} "
            "USING (organization_id = current_setting('app.tenant_id', true)::uuid)"
        )

    # Materialized view for full-text search
    op.execute("""
        CREATE MATERIALIZED VIEW task_search AS
        SELECT t.id, t.project_id, p.organization_id, t.task_number,
               t.title, t.status, t.priority, t.assignee_id,
               to_tsvector('english', t.title || ' ' || coalesce(t.description,'')) AS search_vector
        FROM tasks t
        JOIN projects p ON p.id = t.project_id
    """)
    op.execute("CREATE UNIQUE INDEX ON task_search(id)")
    op.execute("CREATE INDEX idx_task_search_fts ON task_search USING GIN(search_vector)")
    op.execute("CREATE INDEX idx_task_search_org ON task_search(organization_id)")


def downgrade() -> None:
    op.execute("DROP MATERIALIZED VIEW IF EXISTS task_search")
    for table in ["tasks", "sprints", "projects", "organizations", "users"]:
        op.drop_table(table)
