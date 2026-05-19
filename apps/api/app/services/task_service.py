import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.task import Task, TaskComment, TaskCompletion, TaskOutcome, TaskStatus
from app.models.team import TeamMember
from app.models.user import User, UserRole
from app.schemas.task import (
    TaskCommentCreate,
    TaskCompleteRequest,
    TaskCreate,
    TaskStatusUpdate,
    TaskUpdate,
    calculate_due_at,
)


async def _load_task(db: AsyncSession, task_id: uuid.UUID) -> Task:
    result = await db.execute(
        select(Task)
        .where(Task.id == task_id)
        .options(
            selectinload(Task.assignee),
            selectinload(Task.comments).selectinload(TaskComment.author),
            selectinload(Task.completion),
        )
    )
    task = result.scalar_one_or_none()
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"status_code": 404, "message": "Задача не найдена"},
        )
    return task


async def _ensure_assignee_in_team(db: AsyncSession, team_id: uuid.UUID, assignee_id: uuid.UUID) -> None:
    result = await db.execute(
        select(TeamMember).where(TeamMember.team_id == team_id, TeamMember.user_id == assignee_id)
    )
    if result.scalar_one_or_none() is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"status_code": 400, "message": "Исполнитель должен быть членом команды"},
        )


def _ensure_task_editable(task: Task) -> None:
    if task.status in (TaskStatus.COMPLETED, TaskStatus.FAILED):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"status_code": 400, "message": "Завершённую задачу нельзя редактировать"},
        )


async def create_task(db: AsyncSession, team_id: uuid.UUID, payload: TaskCreate) -> Task:
    await _ensure_assignee_in_team(db, team_id, payload.assignee_id)
    task = Task(
        team_id=team_id,
        assignee_id=payload.assignee_id,
        title=payload.title,
        description=payload.description,
        duration_minutes=payload.duration_minutes,
        due_at=calculate_due_at(payload.duration_minutes),
        status=TaskStatus.ASSIGNED,
    )
    db.add(task)
    await db.flush()
    return await _load_task(db, task.id)


async def list_team_tasks(db: AsyncSession, team_id: uuid.UUID) -> list[Task]:
    result = await db.execute(
        select(Task)
        .where(Task.team_id == team_id)
        .options(
            selectinload(Task.assignee),
            selectinload(Task.comments).selectinload(TaskComment.author),
            selectinload(Task.completion),
        )
        .order_by(Task.created_at.desc())
    )
    return list(result.scalars().all())


async def list_my_tasks(db: AsyncSession, user_id: uuid.UUID) -> list[Task]:
    result = await db.execute(
        select(Task)
        .where(Task.assignee_id == user_id)
        .options(
            selectinload(Task.assignee),
            selectinload(Task.comments).selectinload(TaskComment.author),
            selectinload(Task.completion),
        )
        .order_by(Task.due_at.asc())
    )
    return list(result.scalars().all())


async def get_task_for_teamlead(db: AsyncSession, team_id: uuid.UUID, task_id: uuid.UUID) -> Task:
    task = await _load_task(db, task_id)
    if task.team_id != team_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"status_code": 403, "message": "Нет доступа к задаче"},
        )
    return task


async def get_task_for_assignee(db: AsyncSession, user: User, task_id: uuid.UUID) -> Task:
    task = await _load_task(db, task_id)
    if task.assignee_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"status_code": 403, "message": "Нет доступа к задаче"},
        )
    return task


async def update_task(db: AsyncSession, team_id: uuid.UUID, task_id: uuid.UUID, payload: TaskUpdate) -> Task:
    task = await get_task_for_teamlead(db, team_id, task_id)
    _ensure_task_editable(task)

    if payload.assignee_id is not None:
        await _ensure_assignee_in_team(db, team_id, payload.assignee_id)
        task.assignee_id = payload.assignee_id
    if payload.title is not None:
        task.title = payload.title
    if payload.description is not None:
        task.description = payload.description
    if payload.duration_minutes is not None:
        task.duration_minutes = payload.duration_minutes
        task.due_at = calculate_due_at(payload.duration_minutes)

    await db.flush()
    return await _load_task(db, task.id)


async def update_task_status(
    db: AsyncSession, user: User, task_id: uuid.UUID, payload: TaskStatusUpdate
) -> Task:
    task = await get_task_for_assignee(db, user, task_id)
    _ensure_task_editable(task)
    if payload.status == TaskStatus.IN_PROGRESS:
        task.status = TaskStatus.IN_PROGRESS
    await db.flush()
    return await _load_task(db, task.id)


async def add_comment(db: AsyncSession, user: User, task_id: uuid.UUID, payload: TaskCommentCreate) -> TaskComment:
    task = await get_task_for_assignee(db, user, task_id)
    _ensure_task_editable(task)
    comment = TaskComment(task_id=task.id, author_id=user.id, text=payload.text)
    db.add(comment)
    await db.flush()
    result = await db.execute(
        select(TaskComment)
        .where(TaskComment.id == comment.id)
        .options(selectinload(TaskComment.author))
    )
    return result.scalar_one()


async def complete_task(
    db: AsyncSession, user: User, task_id: uuid.UUID, payload: TaskCompleteRequest
) -> Task:
    task = await get_task_for_assignee(db, user, task_id)
    _ensure_task_editable(task)
    if task.completion is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"status_code": 400, "message": "Задача уже завершена"},
        )

    task.status = TaskStatus.COMPLETED if payload.outcome == TaskOutcome.SUCCESS else TaskStatus.FAILED
    completion = TaskCompletion(task_id=task.id, outcome=payload.outcome, comment=payload.comment)
    db.add(completion)
    await db.flush()
    return await _load_task(db, task.id)
