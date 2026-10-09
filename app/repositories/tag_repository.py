from typing import List, Optional

from app.extensions import db
from app.models.task import Tag, Task


class TagRepository:
    """Encapsulates all database operations for the Tag entity."""

    @staticmethod
    def list_ordered() -> List[Tag]:
        return db.session.query(Tag).order_by(Tag.name).all()

    @staticmethod
    def get_by_id(tag_id: int) -> Optional[Tag]:
        return db.session.get(Tag, tag_id)

    @staticmethod
    def get_by_name(name: str) -> Optional[Tag]:
        return db.session.query(Tag).filter(Tag.name == name).first()

    @staticmethod
    def create(name: str) -> Tag:
        tag = Tag(name=name)
        db.session.add(tag)
        db.session.commit()
        return tag

    @staticmethod
    def get_or_create(name: str) -> Tag:
        """Return the existing tag with ``name`` or stage a new one.

        The new tag is added to the session but not committed, so the
        caller controls the transaction boundary.
        """
        tag = TagRepository.get_by_name(name)
        if tag is None:
            tag = Tag(name=name)
            db.session.add(tag)
        return tag

    @staticmethod
    def delete(tag: Tag) -> None:
        db.session.delete(tag)
        db.session.commit()

    @staticmethod
    def attach_to_task(tag: Tag, task: Task) -> None:
        task.tags.append(tag)
        db.session.commit()

    @staticmethod
    def detach_from_task(tag: Tag, task: Task) -> None:
        task.tags.remove(tag)
        db.session.commit()
