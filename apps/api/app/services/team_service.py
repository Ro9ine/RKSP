import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.team import Team, TeamMember
from app.models.user import User, UserRole
from app.schemas.team import TeamMemberCreate
from app.security import get_password_hash


async def get_team_with_members(db: AsyncSession, team: Team) -> Team:
    result = await db.execute(
        select(Team)
        .where(Team.id == team.id)
        .options(selectinload(Team.members).selectinload(TeamMember.user))
    )
    return result.scalar_one()


async def add_team_member(
    db: AsyncSession,
    team: Team,
    payload: TeamMemberCreate,
) -> TeamMember:
    if payload.user_id is not None:
        user_result = await db.execute(select(User).where(User.id == payload.user_id))
        user = user_result.scalar_one_or_none()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"status_code": 404, "message": "Пользователь не найден"},
            )
    else:
        if not payload.email or not payload.password or not payload.full_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"status_code": 400, "message": "Укажите email, пароль и ФИО для нового сотрудника"},
            )
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

    if user.role != UserRole.EMPLOYEE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"status_code": 400, "message": "В команду можно добавить только сотрудника"},
        )

    member_check = await db.execute(select(TeamMember).where(TeamMember.user_id == user.id))
    if member_check.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"status_code": 400, "message": "Пользователь уже в команде"},
        )

    member = TeamMember(team_id=team.id, user_id=user.id)
    db.add(member)
    await db.flush()
    await db.refresh(member, ["user"])
    return member


async def remove_team_member(db: AsyncSession, team: Team, user_id: uuid.UUID) -> None:
    result = await db.execute(
        select(TeamMember).where(TeamMember.team_id == team.id, TeamMember.user_id == user_id)
    )
    member = result.scalar_one_or_none()
    if member is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"status_code": 404, "message": "Участник не найден в команде"},
        )
    await db.delete(member)
