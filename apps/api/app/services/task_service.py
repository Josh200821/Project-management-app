"""Task service."""
from typing import List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.task_repo import TaskRepository
from app.repositories.project_repo import ProjectRepository
from app.schemas.task import TaskCreate, TaskUpdate
from app.workers.notification_tasks import dispatch_mention_notifications


class TaskService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = TaskRepository(session)
        self.project_repo = ProjectRepository(session)

    async def create(self, project_id: UUID, data: TaskCreate, created_by: UUID):
        task_number = await self.project_repo.increment_task_counter(project_id)
        task = await self.repo.create(
            project_id=project_id,
            task_number=task_number,
            created_by=created_by,
            **data.model_dump(exclude_none=True),
        )
        return task

    async def get_board(self, project_id: UUID) -> dict:
        return await self.repo.get_kanban_board(project_id)

    async def list_by_project(self, project_id: UUID, status: Optional[str] = None, offset: int = 0, limit: int = 50):
        return await self.repo.get_by_project(project_id, status, offset, limit)

    async def get(self, task_id: UUID):
        task = await self.repo.get(task_id)
        if not task:
            raise ValueError("Task not found")
        return task

    async def update(self, task_id: UUID, data: TaskUpdate):
        task = await self.repo.get(task_id)
        if not task:
            raise ValueError("Task not found")
        return await self.repo.update(task, **data.model_dump(exclude_none=True))

    async def delete(self, task_id: UUID) -> None:
        task = await self.repo.get(task_id)
        if task:
            await self.repo.delete(task)

    async def search(self, org_id: UUID, query: str) -> list:
        return await self.repo.search(org_id, query)
