"""Shared response envelope, pagination, and error schemas."""
from typing import Generic, List, Optional, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class Meta(BaseModel):
    total: Optional[int] = None
    page: Optional[int] = None
    per_page: Optional[int] = None
    pages: Optional[int] = None


class ApiResponse(BaseModel, Generic[T]):
    data: T
    meta: Optional[Meta] = None
    errors: List[str] = []


class ErrorResponse(BaseModel):
    data: None = None
    errors: List[str]


class PaginationParams(BaseModel):
    page: int = 1
    per_page: int = 20

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.per_page
