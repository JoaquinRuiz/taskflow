from typing import List, Optional

from app.extensions import db
from app.models.project import Project


class ProjectRepository:
    """Encapsulates all database operations for the Project entity."""

    @staticmethod
    def list(owner_id: Optional[int] = None) -> List[Project]:
        query = db.session.query(Project).order_by(Project.created_at.desc())
        if owner_id:
            query = query.filter(Project.owner_id == owner_id)
        return query.all()

    @staticmethod
    def get_by_id(project_id: int) -> Optional[Project]:
        return db.session.get(Project, project_id)

    @staticmethod
    def get_name_conflict(
        name: str, owner_id: int, exclude_id: Optional[int] = None
    ) -> Optional[Project]:
        query = db.session.query(Project).filter(
            Project.name == name,
            Project.owner_id == owner_id,
        )
        if exclude_id is not None:
            query = query.filter(Project.id != exclude_id)
        return query.first()

    @staticmethod
    def create(name: str, description: str, owner_id: int) -> Project:
        project = Project(
            name=name,
            description=description,
            owner_id=owner_id,
        )
        db.session.add(project)
        db.session.commit()
        return project

    @staticmethod
    def update(project: Project) -> Project:
        db.session.commit()
        return project

    @staticmethod
    def delete(project: Project) -> None:
        db.session.delete(project)
        db.session.commit()
