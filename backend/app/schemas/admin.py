from datetime import datetime

from pydantic import BaseModel

from backend.app.core.roles import UserRole


class AdminUserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: UserRole
    created_at: datetime | None = None

    class Config:
        from_attributes = True


class UpdateUserRoleRequest(BaseModel):
    role: UserRole


class PaginatedUsersResponse(BaseModel):
    page: int
    limit: int
    total: int
    total_pages: int
    items: list[AdminUserResponse]