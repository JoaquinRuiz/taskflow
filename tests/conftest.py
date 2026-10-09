import pytest

from app import create_app
from app.config import TestConfig
from app.extensions import db as _db
from app.models import User, Project, Task, Tag


@pytest.fixture(scope="session")
def app():
    app = create_app(TestConfig)
    return app


@pytest.fixture(autouse=True)
def db(app):
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.rollback()
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def sample_user(db):
    user = User(username="alice", email="alice@example.com")
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def second_user(db):
    user = User(username="bob", email="bob@example.com")
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def sample_project(db, sample_user):
    project = Project(name="TaskFlow", description="A task manager", owner_id=sample_user.id)
    db.session.add(project)
    db.session.commit()
    return project


@pytest.fixture
def sample_task(db, sample_project, sample_user):
    task = Task(
        title="Write tests",
        description="Write unit tests for the API",
        project_id=sample_project.id,
        assignee_id=sample_user.id,
        status=Task.STATUS_TODO,
        priority=Task.PRIORITY_HIGH,
    )
    db.session.add(task)
    db.session.commit()
    return task


@pytest.fixture
def sample_tag(db):
    tag = Tag(name="urgent")
    db.session.add(tag)
    db.session.commit()
    return tag
