import uuid
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.team import Team, TeamMember
from app.models.user import User, UserRole
from app.security import decode_access_token

security_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"status_code": 401, "message": "Требуется авторизация"},
        )
    try:
        payload = decode_access_token(credentials.credentials)
        user_id = uuid.UUID(payload["sub"])
    except (ValueError, KeyError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"status_code": 401, "message": "Недействительный токен"},
        ) from None

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"status_code": 401, "message": "Пользователь не найден"},
        )
    return user


async def require_teamlead(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    if current_user.role != UserRole.TEAMLEAD:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"status_code": 403, "message": "Доступ только для тимлида"},
        )
    return current_user


async def require_employee(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    if current_user.role != UserRole.EMPLOYEE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"status_code": 403, "message": "Доступ только для сотрудника"},
        )
    return current_user


async def get_teamlead_team(
    teamlead: Annotated[User, Depends(require_teamlead)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Team:
    result = await db.execute(
        select(Team)
        .where(Team.teamlead_id == teamlead.id)
        .options(selectinload(Team.members).selectinload(TeamMember.user))
    )
    team = result.scalar_one_or_none()
    if team is None:
        team = Team(name=f"Команда {teamlead.full_name}", teamlead_id=teamlead.id)
        db.add(team)
        await db.flush()
        await db.refresh(team)
    return team


CurrentUser = Annotated[User, Depends(get_current_user)]
TeamleadUser = Annotated[User, Depends(require_teamlead)]
EmployeeUser = Annotated[User, Depends(require_employee)]
TeamleadTeam = Annotated[Team, Depends(get_teamlead_team)]
DbSession = Annotated[AsyncSession, Depends(get_db)]
