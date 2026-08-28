"""Analytics schemas."""

from pydantic import BaseModel


class VelocityPoint(BaseModel):
    sprint_name: str
    completed_points: int
    planned_points: int


class BurndownPoint(BaseModel):
    day: str
    remaining: int
    ideal: float


class TaskStatusDistribution(BaseModel):
    status: str
    count: int


class TeamMemberUtilization(BaseModel):
    user_id: str
    full_name: str
    open_tasks: int
    hours_logged: float


class ProjectAnalytics(BaseModel):
    total_tasks: int
    completed_tasks: int
    open_tasks: int
    overdue_tasks: int
    velocity: list[VelocityPoint]
    status_distribution: list[TaskStatusDistribution]
    team_utilization: list[TeamMemberUtilization]
