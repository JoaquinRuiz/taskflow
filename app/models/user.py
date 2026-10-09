from datetime import datetime, timezone

from app.extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc)
    )

    owned_projects = db.relationship(
        "Project", back_populates="owner", lazy="select"
    )
    assigned_tasks = db.relationship(
        "Task", back_populates="assignee", lazy="select"
    )

    def __repr__(self):
        return f"<User {self.username}>"
