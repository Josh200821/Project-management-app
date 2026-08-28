"""Generic async CRUD base repository."""

from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base


class BaseRepository[ModelT: Base]:
    def __init__(self, model: type[ModelT], session: AsyncSession) -> None:
        self.model = model
        self.session = session

    async def get(self, id: UUID) -> ModelT | None:
        result = await self.session.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()

    async def get_all(self, offset: int = 0, limit: int = 20) -> list[ModelT]:
        result = await self.session.execute(select(self.model).offset(offset).limit(limit))
        return list(result.scalars().all())

    async def list(self, offset: int = 0, limit: int = 100, **filters: Any) -> list[ModelT]:
        """Simple equality-filtered listing, e.g. `repo.list(status="active")`."""
        query = select(self.model)
        for field, value in filters.items():
            query = query.where(getattr(self.model, field) == value)
        query = query.offset(offset).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def count(self) -> int:
        result = await self.session.execute(select(func.count()).select_from(self.model))
        return result.scalar_one()

    async def create(self, **kwargs: Any) -> ModelT:
        obj = self.model(**kwargs)
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def update(self, obj: ModelT, **kwargs: Any) -> ModelT:
        for key, value in kwargs.items():
            if value is not None:
                setattr(obj, key, value)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def delete(self, obj: ModelT) -> None:
        await self.session.delete(obj)
        await self.session.flush()
