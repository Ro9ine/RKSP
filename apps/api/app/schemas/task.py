import uuid
from datetime import datetime, timedelta, timezone

from pydantic import BaseModel, Field, field_validator, model_validator

from app.models.task import TaskOutcome, TaskStatus
from app.schemas.user import UserResponse

MIN_DURATION_MINUTES = 60
MAX_DURATION_MINUTES = 14 * 24 * 60


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str = Field(default="", max_length=5000)
    assignee_id: uuid.UUID
    duration_minutes: int = Field(ge=MIN_DURATION_MINUTES, le=MAX_DURATION_MINUTES)

    @field_validator("duration_minutes")
    @classmethod
    def validate_duration(cls, value: int) -> int:
        if value < MIN_DURATION_MINUTES or value > MAX_DURATION_MINUTES:
            raise ValueError(
                f"Срок выполнения должен быть от {MIN_DURATION_MINUTES} минут до {MAX_DURATION_MINUTES} минут"
            )
        return value


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=5000)
    assignee_id: uuid.UUID | None = None
    duration_minutes: int | None = Field(default=None, ge=MIN_DURATION_MINUTES, le=MAX_DURATION_MINUTES)


class TaskStatusUpdate(BaseModel):
    status: TaskStatus

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: TaskStatus) -> TaskStatus:
        if value not in (TaskStatus.IN_PROGRESS, TaskStatus.ASSIGNED):
            raise ValueError("Сотрудник может перевести задачу только в IN_PROGRESS")
        return value


class TaskCommentCreate(BaseModel):
    text: str = Field(min_length=1, max_length=2000)


class TaskCompleteRequest(BaseModel):
    outcome: TaskOutcome
    comment: str = Field(min_length=1, max_length=2000)


class TaskCommentResponse(BaseModel):
    id: uuid.UUID
    task_id: uuid.UUID
    author_id: uuid.UUID
    text: str
    created_at: datetime
    author: UserResponse | None = None

    model_config = {"from_attributes": True}


class TaskCompletionResponse(BaseModel):
    id: uuid.UUID
    outcome: TaskOutcome
    comment: str
    completed_at: datetime

    model_config = {"from_attributes": True}


class TaskResponse(BaseModel):
    id: uuid.UUID
    team_id: uuid.UUID
    assignee_id: uuid.UUID
    title: str
    description: str
    status: TaskStatus
    duration_minutes: int
    due_at: datetime
    created_at: datetime
    updated_at: datetime
    assignee: UserResponse | None = None
    comments: list[TaskCommentResponse] = []
    completion: TaskCompletionResponse | None = None

    model_config = {"from_attributes": True}

    @model_validator(mode="before")
    @classmethod
    def compute_due_if_needed(cls, data: object) -> object:
        return data


def calculate_due_at(duration_minutes: int) -> datetime:
    return datetime.now(timezone.utc) + timedelta(minutes=duration_minutes)
