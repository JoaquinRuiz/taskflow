from typing import List, Optional, Tuple

from app.extensions import db
from app.models.user import User


class UserRepository:
    """Encapsulates all database operations for the User entity."""

    @staticmethod
    def list_paginated(page: int, per_page: int) -> Tuple[List[User], int]:
        query = db.session.query(User).order_by(User.created_at.desc())
        total = query.count()
        users = query.offset((page - 1) * per_page).limit(per_page).all()
        return users, total

    @staticmethod
    def get_by_id(user_id: int) -> Optional[User]:
        return db.session.get(User, user_id)

    @staticmethod
    def get_by_username_or_email(username: str, email: str) -> Optional[User]:
        return (
            db.session.query(User)
            .filter((User.username == username) | (User.email == email))
            .first()
        )

    @staticmethod
    def get_username_conflict(
        username: str, exclude_id: Optional[int] = None
    ) -> Optional[User]:
        query = db.session.query(User).filter(User.username == username)
        if exclude_id is not None:
            query = query.filter(User.id != exclude_id)
        return query.first()

    @staticmethod
    def get_email_conflict(
        email: str, exclude_id: Optional[int] = None
    ) -> Optional[User]:
        query = db.session.query(User).filter(User.email == email)
        if exclude_id is not None:
            query = query.filter(User.id != exclude_id)
        return query.first()

    @staticmethod
    def create(username: str, email: str) -> User:
        user = User(username=username, email=email)
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def update(user: User) -> User:
        db.session.commit()
        return user

    @staticmethod
    def delete(user: User) -> None:
        db.session.delete(user)
        db.session.commit()
