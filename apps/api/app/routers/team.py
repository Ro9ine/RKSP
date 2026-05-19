import uuid

from fastapi import APIRouter, status

from app.deps import DbSession, TeamleadTeam, TeamleadUser
from app.schemas.team import TeamMemberCreate, TeamMemberResponse, TeamResponse
from app.services import team_service

router = APIRouter(prefix="/team", tags=["team"])


@router.get("", response_model=TeamResponse)
async def get_team(team: TeamleadTeam, db: DbSession) -> TeamResponse:
    loaded = await team_service.get_team_with_members(db, team)
    return loaded


@router.post("/members", response_model=TeamMemberResponse, status_code=status.HTTP_201_CREATED)
async def add_member(
    payload: TeamMemberCreate,
    db: DbSession,
    teamlead: TeamleadUser,
    team: TeamleadTeam,
) -> TeamMemberResponse:
    member = await team_service.add_team_member(db, team, payload)
    return member


@router.delete("/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(
    user_id: uuid.UUID,
    db: DbSession,
    teamlead: TeamleadUser,
    team: TeamleadTeam,
) -> None:
    await team_service.remove_team_member(db, team, user_id)
