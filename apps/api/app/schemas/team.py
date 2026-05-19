import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.user import UserResponse


class TeamResponse(BaseModel):
    id: uuid.UUID
    name: str
    teamlead_id: uuid.UUID
    created_at: datetime
    members: list["TeamMemberResponse"] = []

    model_config = {"from_attributes": True}


class TeamMemberResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    joined_at: datetime
    user: UserResponse | None = None

    model_config = {"from_attributes": True}


class TeamMemberCreate(BaseModel):
    user_id: uuid.UUID | None = None
    email: str | None = None
    password: str | None = Field(default=None, min_length=6, max_length=128)
    full_name: str | None = Field(default=None, min_length=1, max_length=255)
