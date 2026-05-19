"""Заполнение БД тестовыми данными для разработки и демонстрации."""

import asyncio
import sys
from sqlalchemy import select

sys.path.insert(0, ".")

from app.database import async_session_factory
from app.models.task import Task, TaskComment, TaskCompletion, TaskOutcome, TaskStatus
from app.models.team import Team, TeamMember
from app.models.user import User, UserRole
from app.schemas.task import calculate_due_at
from app.security import get_password_hash

PASSWORD = "password123"


async def seed() -> None:
    async with async_session_factory() as session:
        existing = await session.execute(select(User).where(User.email == "lead@example.com"))
        if existing.scalar_one_or_none():
            print("Seed уже выполнен, пропуск.")
            return

        teamlead = User(
            email="lead@example.com",
            hashed_password=get_password_hash(PASSWORD),
            full_name="Иван Тимлидов",
            role=UserRole.TEAMLEAD,
        )
        session.add(teamlead)
        await session.flush()

        team = Team(name="Команда разработки", teamlead_id=teamlead.id)
        session.add(team)
        await session.flush()

        employees_data = [
            ("anna@example.com", "Анна Сотрудникова"),
            ("petr@example.com", "Пётр Разработчик"),
            ("maria@example.com", "Мария Тестерова"),
        ]
        employees: list[User] = []
        for email, name in employees_data:
            employee = User(
                email=email,
                hashed_password=get_password_hash(PASSWORD),
                full_name=name,
                role=UserRole.EMPLOYEE,
            )
            session.add(employee)
            await session.flush()
            session.add(TeamMember(team_id=team.id, user_id=employee.id))
            employees.append(employee)

        tasks_config = [
            ("Настроить CI", "Подключить пайплайн сборки", employees[0], 480, TaskStatus.ASSIGNED),
            ("Код-ревью API", "Проверить эндпоинты задач", employees[1], 240, TaskStatus.IN_PROGRESS),
            ("Написать тесты", "Покрыть сервисы unit-тестами", employees[0], 1440, TaskStatus.ASSIGNED),
            ("Документация", "Обновить README", employees[2], 120, TaskStatus.COMPLETED),
            ("Рефакторинг UI", "Упростить формы", employees[1], 720, TaskStatus.FAILED),
            ("Интеграция фронта", "Подключить TanStack Query", employees[2], 360, TaskStatus.ASSIGNED),
            ("Fuzz-тестирование", "Прогнать schemathesis", employees[0], 180, TaskStatus.ASSIGNED),
        ]

        for title, desc, assignee, duration, status in tasks_config:
            task = Task(
                team_id=team.id,
                assignee_id=assignee.id,
                title=title,
                description=desc,
                duration_minutes=duration,
                due_at=calculate_due_at(duration),
                status=status,
            )
            session.add(task)
            await session.flush()

            if status == TaskStatus.COMPLETED:
                session.add(
                    TaskCompletion(
                        task_id=task.id,
                        outcome=TaskOutcome.SUCCESS,
                        comment="Выполнено в срок",
                    )
                )
            elif status == TaskStatus.FAILED:
                session.add(
                    TaskCompletion(
                        task_id=task.id,
                        outcome=TaskOutcome.FAILURE,
                        comment="Не хватило времени на рефакторинг",
                    )
                )

            if status == TaskStatus.IN_PROGRESS:
                session.add(
                    TaskComment(
                        task_id=task.id,
                        author_id=assignee.id,
                        text="Начал работу над задачей",
                    )
                )

        await session.commit()
        print("Seed выполнен успешно.")
        print(f"Тимлид: lead@example.com / {PASSWORD}")
        print(f"Сотрудники: anna@example.com, petr@example.com, maria@example.com / {PASSWORD}")


if __name__ == "__main__":
    asyncio.run(seed())
