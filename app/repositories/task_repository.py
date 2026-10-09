from typing import List, Optional

from app.extensions import db
from app.models.task import Task, Tag
from app.repositories.tag_repository import TagRepository


class TaskRepository:
    """Encapsulates all database operations for the Task entity."""

    @staticmethod
    def list(
        project_id: Optional[int] = None,
        assignee_id: Optional[int] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        tag: Optional[str] = None,
    ) -> List[Task]:
        query = db.session.query(Task).order_by(Task.created_at.desc())
        if project_id:
            query = query.filter(Task.project_id == project_id)
        if assignee_id:
            query = query.filter(Task.assignee_id == assignee_id)
        if status:
            query = query.filter(Task.status == status)
        if priority:
            query = query.filter(Task.priority == priority)
        if tag:
            query = query.filter(Task.tags.any(Tag.name == tag))
        return query.all()

    @staticmethod
    def get_by_id(task_id: int) -> Optional[Task]:
        return db.session.get(Task, task_id)

    @staticmethod
    def create(
        title: str,
        description: str,
        status: str,
        priority: str,
        project_id: int,
        assignee_id: Optional[int] = None,
        tag_names: Optional[List[str]] = None,
    ) -> Task:
        task = Task(
            title=title,
            description=description,
            status=status,
            priority=priority,
            project_id=project_id,
            assignee_id=assignee_id,
        )
        db.session.add(task)

        for name in tag_names or []:
            task.tags.append(TagRepository.get_or_create(name))

        db.session.commit()
        return task

    @staticmethod
    def set_tags(task: Task, tag_names: List[str]) -> None:
        """Replace the task's tags with the given names (no commit)."""
        task.tags.clear()
        for name in tag_names:
            task.tags.append(TagRepository.get_or_create(name))

    @staticmethod
    def update(task: Task) -> Task:
        db.session.commit()
        return task

    @staticmethod
    def delete(task: Task) -> None:
        db.session.delete(task)
        db.session.commit()

    @staticmethod
    def _base_query(project_id: Optional[int] = None):
        query = db.session.query(Task)
        if project_id:
            query = query.filter(Task.project_id == project_id)
        return query

    @staticmethod
    def count(project_id: Optional[int] = None) -> int:
        return TaskRepository._base_query(project_id).count()

    @staticmethod
    def count_by_status(status: str, project_id: Optional[int] = None) -> int:
        return (
            TaskRepository._base_query(project_id)
            .filter(Task.status == status)
            .count()
        )

    @staticmethod
    def count_by_priority(
        priority: str, project_id: Optional[int] = None
    ) -> int:
        return (
            TaskRepository._base_query(project_id)
            .filter(Task.priority == priority)
            .count()
        )

    @staticmethod
    def count_unassigned(project_id: Optional[int] = None) -> int:
        return (
            TaskRepository._base_query(project_id)
            .filter(Task.assignee_id.is_(None))
            .count()
        )
