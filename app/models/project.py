from datetime import datetime, timezone

from app.extensions import db


class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, default="")
    owner_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False
    )
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc)
    )

    owner = db.relationship("User", back_populates="owned_projects")
    tasks = db.relationship(
        "Task", back_populates="project", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Project {self.name}>"
