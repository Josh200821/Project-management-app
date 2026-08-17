"""Task repository with full-text search."""
from typing import List, Optional
from uuid import UUID
from sqlalchemy import select, text, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.task import Task
from app.repositories.base import BaseRepository


class TaskRepository(BaseRepository[Task]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Task, session)

    async def get_by_project(
        self, project_id: UUID, status: Optional[str] = None,
        offset: int = 0, limit: int = 50
    ) -> List[Task]:
        q = select(Task).where(Task.project_id == project_id)
        if status:
            q = q.where(Task.status == status)
        q = q.order_by(Task.board_order).offset(offset).limit(limit)
        result = await self.session.execute(q)
        return list(result.scalars().all())

    async def get_by_sprint(self, sprint_id: UUID) -> List[Task]:
        result = await self.session.execute(
            select(Task).where(Task.sprint_id == sprint_id).order_by(Task.board_order)
        )
        return list(result.scalars().all())

    async def search(self, org_id: UUID, query: str, limit: int = 20) -> List[Task]:
        result = await self.session.execute(
            text("""
                SELECT t.* FROM tasks t
                JOIN projects p ON p.id = t.project_id
                WHERE p.organization_id = :org_id
                AND to_tsvector('english', t.title || ' ' || COALESCE(t.description, ''))
                    @@ plainto_tsquery('english', :query)
                ORDER BY ts_rank(
                    to_tsvector('english', t.title || ' ' || COALESCE(t.description, '')),
                    plainto_tsquery('english', :query)
                ) DESC
                LIMIT :limit
            """),
            {"org_id": str(org_id), "query": query, "limit": limit}
        )
        return list(result.mappings().all())

    async def get_kanban_board(self, project_id: UUID) -> dict:
        tasks = await self.get_by_project(project_id, limit=500)
        board: dict = {}
        for task in tasks:
            board.setdefault(task.status, []).append(task)
        return board
