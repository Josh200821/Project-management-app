"""Shared response envelope, pagination, and error schemas."""

from pydantic import BaseModel


class Meta(BaseModel):
    total: int | None = None
    page: int | None = None
    per_page: int | None = None
    pages: int | None = None


class ApiResponse[T](BaseModel):
    data: T
    meta: Meta | None = None
    errors: list[str] = []


class ErrorResponse(BaseModel):
    data: None = None
    errors: list[str]


class PaginationParams(BaseModel):
    page: int = 1
    per_page: int = 20

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.per_page
