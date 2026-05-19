from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.deps import CurrentUser, DbSession, TeamleadTeam, TeamleadUser
from app.models.team import TeamMember
from app.models.user import User, UserRole
from app.schemas.team import TeamMemberCreate
from app.schemas.user import EmployeeCreate, UserResponse
from app.security import get_password_hash
from app.services import team_service

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: CurrentUser) -> User:
    return current_user


@router.post("/employees", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_employee(
    payload: EmployeeCreate,
    db: DbSession,
    teamlead: TeamleadUser,
    team: TeamleadTeam,
) -> User:
    existing = await db.execute(select(User).where(User.email == payload.email))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"status_code": 400, "message": "Email уже занят"},
        )
    user = User(
        email=payload.email,
        hashed_password=get_password_hash(payload.password),
        full_name=payload.full_name,
        role=UserRole.EMPLOYEE,
    )
    db.add(user)
    await db.flush()
    await team_service.add_team_member(
        db,
        team,
        TeamMemberCreate(user_id=user.id),
    )
    return user
