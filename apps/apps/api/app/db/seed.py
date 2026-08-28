"""Development seed data."""

import asyncio

from app.core.security import hash_password
from app.db.base import async_session_factory
from app.db.models.organization import Organization
from app.db.models.organization_member import OrganizationMember
from app.db.models.project import Project
from app.db.models.sprint import Sprint
from app.db.models.task import Task
from app.db.models.user import User


async def seed():
    async with async_session_factory() as session:
        # Admin user
        admin = User(
            email="admin@example.com",
            password_hash=hash_password("Admin1234!"),
            full_name="Admin User",
            is_active=True,
        )
        session.add(admin)
        await session.flush()

        # Demo user
        demo = User(
            email="demo@example.com",
            password_hash=hash_password("Demo1234!"),
            full_name="Demo User",
            is_active=True,
        )
        session.add(demo)
        await session.flush()

        # Organization
        org = Organization(
            name="Acme Corp",
            slug="acme-corp",
            plan="pro",
        )
        session.add(org)
        await session.flush()

        # Members
        for user, role in [(admin, "admin"), (demo, "member")]:
            session.add(OrganizationMember(organization_id=org.id, user_id=user.id, role=role))

        # Project
        project = Project(
            organization_id=org.id,
            name="Platform Rewrite",
            slug="platform-rewrite",
            description="Complete rewrite of the legacy platform",
            created_by=admin.id,
            task_counter=0,
        )
        session.add(project)
        await session.flush()

        # Sprint
        from datetime import date, timedelta

        sprint = Sprint(
            project_id=project.id,
            name="Sprint 1",
            goal="Ship MVP auth and project management",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=14),
            status="active",
            capacity_points=40,
        )
        session.add(sprint)
        await session.flush()

        # Tasks
        tasks_data = [
            ("Set up FastAPI project", "todo", "high", 3),
            ("Implement JWT auth", "in_progress", "critical", 5),
            ("Build Kanban board", "todo", "high", 8),
            ("Database migrations", "done", "high", 3),
            ("Write unit tests", "todo", "medium", 5),
            ("Deploy to staging", "todo", "high", 3),
        ]
        for i, (title, status, priority, points) in enumerate(tasks_data):
            project.task_counter += 1
            task = Task(
                project_id=project.id,
                task_number=project.task_counter,
                title=title,
                status=status,
                priority=priority,
                story_points=points,
                assignee_id=admin.id,
                created_by=admin.id,
                sprint_id=sprint.id,
                board_order=float(i),
            )
            session.add(task)

        await session.commit()
        print("Seed complete!")
        print("  Admin: admin@example.com / Admin1234!")
        print("  Demo:  demo@example.com  / Demo1234!")
        print(f"  Org:   {org.id}")
        print(f"  Project: {project.id}")


if __name__ == "__main__":
    asyncio.run(seed())
