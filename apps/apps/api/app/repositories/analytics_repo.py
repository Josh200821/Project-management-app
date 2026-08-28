"""Analytics repository — always uses read replica when available."""

from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class AnalyticsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_velocity(self, project_id: UUID) -> list[dict]:
        result = await self.session.execute(
            text("""
                SELECT s.name as sprint_name,
                       COALESCE(SUM(t.story_points)
                           FILTER (WHERE t.status='done'), 0) as completed_points,
                       COALESCE(s.capacity_points, 0) as planned_points
                FROM sprints s
                LEFT JOIN tasks t ON t.sprint_id = s.id
                WHERE s.project_id = :project_id
                GROUP BY s.id, s.name, s.capacity_points, s.created_at
                ORDER BY s.created_at ASC
                LIMIT 10
            """),
            {"project_id": str(project_id)},
        )
        return [dict(r) for r in result.mappings()]

    async def get_task_status_distribution(self, project_id: UUID) -> list[dict]:
        result = await self.session.execute(
            text("""
                SELECT status, COUNT(*) as count
                FROM tasks WHERE project_id = :project_id
                GROUP BY status
            """),
            {"project_id": str(project_id)},
        )
        return [dict(r) for r in result.mappings()]

    async def get_team_utilization(self, org_id: UUID) -> list[dict]:
        result = await self.session.execute(
            text("""
                SELECT u.id as user_id, u.full_name,
                       COUNT(t.id)
                           FILTER (WHERE t.status NOT IN ('done','cancelled')) as open_tasks,
                       COALESCE(SUM(te.duration_seconds)/3600.0, 0) as hours_logged
                FROM users u
                JOIN organization_members om ON om.user_id = u.id
                LEFT JOIN tasks t ON t.assignee_id = u.id
                LEFT JOIN time_entries te ON te.user_id = u.id
                WHERE om.organization_id = :org_id
                GROUP BY u.id, u.full_name
                ORDER BY open_tasks DESC
            """),
            {"org_id": str(org_id)},
        )
        return [dict(r) for r in result.mappings()]
