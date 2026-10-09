from datetime import datetime, timezone

from app.extensions import db


task_tags = db.Table(
    "task_tags",
    db.Column("task_id", db.Integer, db.ForeignKey("tasks.id"), primary_key=True),
    db.Column("tag_id", db.Integer, db.ForeignKey("tags.id"), primary_key=True),
)


class Tag(db.Model):
    __tablename__ = "tags"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    tasks = db.relationship(
        "Task", secondary=task_tags, back_populates="tags", lazy="select"
    )

    def __repr__(self):
        return f"<Tag {self.name}>"


class Task(db.Model):
    __tablename__ = "tasks"

    STATUS_TODO = "todo"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_DONE = "done"
    VALID_STATUSES = [STATUS_TODO, STATUS_IN_PROGRESS, STATUS_DONE]

    PRIORITY_LOW = "low"
    PRIORITY_MEDIUM = "medium"
    PRIORITY_HIGH = "high"
    VALID_PRIORITIES = [PRIORITY_LOW, PRIORITY_MEDIUM, PRIORITY_HIGH]

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default="")
    status = db.Column(db.String(20), default=STATUS_TODO, nullable=False)
    priority = db.Column(db.String(20), default=PRIORITY_MEDIUM, nullable=False)
    project_id = db.Column(
        db.Integer, db.ForeignKey("projects.id"), nullable=False
    )
    assignee_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=True
    )
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    project = db.relationship("Project", back_populates="tasks")
    assignee = db.relationship("User", back_populates="assigned_tasks")
    tags = db.relationship(
        "Tag", secondary=task_tags, back_populates="tasks", lazy="select"
    )

    def __repr__(self):
        return f"<Task {self.title}>"
