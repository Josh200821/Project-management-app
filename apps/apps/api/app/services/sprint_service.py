"""Sprint service."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.sprint_repo import SprintRepository
from app.repositories.task_repo import TaskRepository
from app.schemas.sprint import SprintCreate, SprintUpdate


class SprintService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = SprintRepository(session)
        self.task_repo = TaskRepository(session)

    async def create(self, project_id: UUID, data: SprintCreate):
        return await self.repo.create(project_id=project_id, **data.model_dump(exclude_none=True))

    async def list_by_project(self, project_id: UUID):
        return await self.repo.get_by_project(project_id)

    async def get(self, sprint_id: UUID):
        sprint = await self.repo.get(sprint_id)
        if not sprint:
            raise ValueError("Sprint not found")
        return sprint

    async def update(self, sprint_id: UUID, data: SprintUpdate):
        sprint = await self.repo.get(sprint_id)
        if not sprint:
            raise ValueError("Sprint not found")
        return await self.repo.update(sprint, **data.model_dump(exclude_none=True))

    async def close(self, sprint_id: UUID, route_to: str = "backlog"):
        """Close sprint and route incomplete tasks."""
        sprint = await self.repo.get(sprint_id)
        if not sprint:
            raise ValueError("Sprint not found")
        incomplete = await self.task_repo.get_by_sprint(sprint_id)
        for task in incomplete:
            if task.status != "done" and route_to == "backlog":
                task.sprint_id = None
                # else: would need next sprint ID
        await self.repo.update(sprint, status="closed")
        await self.repo.session.flush()
        return sprint

    async def get_burndown(self, sprint_id: UUID) -> list[dict]:
        """Return daily remaining story points for the sprint."""
        # Simplified: real impl would query task history
        sprint = await self.repo.get(sprint_id)
        if not sprint or not sprint.start_date or not sprint.end_date:
            return []
        tasks = await self.task_repo.get_by_sprint(sprint_id)
        total = sum(t.story_points or 1 for t in tasks)
        done = sum(t.story_points or 1 for t in tasks if t.status == "done")
        return [
            {"day": str(sprint.start_date), "remaining": total, "ideal": float(total)},
            {"day": str(sprint.end_date), "remaining": total - done, "ideal": 0.0},
        ]
