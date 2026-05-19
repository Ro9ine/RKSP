import uuid

from fastapi import APIRouter, status

from app.deps import DbSession, EmployeeUser, TeamleadTeam, TeamleadUser
from app.schemas.task import (
    TaskCommentCreate,
    TaskCommentResponse,
    TaskCompleteRequest,
    TaskCreate,
    TaskResponse,
    TaskStatusUpdate,
    TaskUpdate,
)
from app.services import task_service

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    payload: TaskCreate,
    db: DbSession,
    teamlead: TeamleadUser,
    team: TeamleadTeam,
) -> TaskResponse:
    return await task_service.create_task(db, team.id, payload)


@router.get("", response_model=list[TaskResponse])
async def list_tasks(
    db: DbSession,
    teamlead: TeamleadUser,
    team: TeamleadTeam,
) -> list[TaskResponse]:
    return await task_service.list_team_tasks(db, team.id)


@router.get("/my", response_model=list[TaskResponse])
async def list_my_tasks(db: DbSession, employee: EmployeeUser) -> list[TaskResponse]:
    return await task_service.list_my_tasks(db, employee.id)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: uuid.UUID,
    db: DbSession,
    teamlead: TeamleadUser,
    team: TeamleadTeam,
) -> TaskResponse:
    return await task_service.get_task_for_teamlead(db, team.id, task_id)


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: uuid.UUID,
    payload: TaskUpdate,
    db: DbSession,
    teamlead: TeamleadUser,
    team: TeamleadTeam,
) -> TaskResponse:
    return await task_service.update_task(db, team.id, task_id, payload)


@router.patch("/{task_id}/status", response_model=TaskResponse)
async def update_status(
    task_id: uuid.UUID,
    payload: TaskStatusUpdate,
    db: DbSession,
    employee: EmployeeUser,
) -> TaskResponse:
    return await task_service.update_task_status(db, employee, task_id, payload)


@router.post("/{task_id}/comments", response_model=TaskCommentResponse, status_code=status.HTTP_201_CREATED)
async def add_comment(
    task_id: uuid.UUID,
    payload: TaskCommentCreate,
    db: DbSession,
    employee: EmployeeUser,
) -> TaskCommentResponse:
    return await task_service.add_comment(db, employee, task_id, payload)


@router.post("/{task_id}/complete", response_model=TaskResponse)
async def complete_task(
    task_id: uuid.UUID,
    payload: TaskCompleteRequest,
    db: DbSession,
    employee: EmployeeUser,
) -> TaskResponse:
    return await task_service.complete_task(db, employee, task_id, payload)
