"""Analytics service."""

from datetime import UTC
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.analytics_repo import AnalyticsRepository
from app.repositories.task_repo import TaskRepository
from app.schemas.analytics import ProjectAnalytics


class AnalyticsService:
    def __init__(self, session: AsyncSession) -> None:
        self.analytics_repo = AnalyticsRepository(session)
        self.task_repo = TaskRepository(session)

    async def get_project_analytics(self, project_id: UUID, org_id: UUID) -> ProjectAnalytics:
        tasks = await self.task_repo.get_by_project(project_id, limit=10000)
        total = len(tasks)
        completed = sum(1 for t in tasks if t.status == "done")
        open_tasks = sum(1 for t in tasks if t.status not in ("done", "cancelled"))

        from datetime import datetime

        overdue = sum(
            1 for t in tasks if t.due_date and t.status != "done" and t.due_date < datetime.now(UTC)
        )

        velocity = await self.analytics_repo.get_velocity(project_id)
        status_dist = await self.analytics_repo.get_task_status_distribution(project_id)
        utilization = await self.analytics_repo.get_team_utilization(org_id)

        return ProjectAnalytics(
            total_tasks=total,
            completed_tasks=completed,
            open_tasks=open_tasks,
            overdue_tasks=overdue,
            velocity=velocity,
            status_distribution=status_dist,
            team_utilization=utilization,
        )
