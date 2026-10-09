"""Unit tests that exercise the repository layer directly (no HTTP)."""

from app.models import Project, Task, Tag, User
from app.repositories import (
    ProjectRepository,
    TagRepository,
    TaskRepository,
    UserRepository,
)


class TestUserRepository:
    def test_create(self, db):
        user = UserRepository.create("charlie", "charlie@example.com")
        assert user.id is not None
        assert user.username == "charlie"
        assert db.session.get(User, user.id) is not None

    def test_get_by_id(self, sample_user):
        found = UserRepository.get_by_id(sample_user.id)
        assert found is not None
        assert found.username == "alice"

    def test_get_by_id_missing(self, db):
        assert UserRepository.get_by_id(9999) is None

    def test_list_paginated(self, sample_user, second_user):
        users, total = UserRepository.list_paginated(page=1, per_page=20)
        assert total == 2
        assert len(users) == 2

    def test_list_paginated_limits_results(self, sample_user, second_user):
        users, total = UserRepository.list_paginated(page=1, per_page=1)
        assert total == 2
        assert len(users) == 1

    def test_get_by_username_or_email(self, sample_user):
        assert UserRepository.get_by_username_or_email("alice", "x@x.com") is not None
        assert UserRepository.get_by_username_or_email("x", "alice@example.com") is not None
        assert UserRepository.get_by_username_or_email("x", "x@x.com") is None

    def test_username_conflict_excludes_self(self, sample_user, second_user):
        assert UserRepository.get_username_conflict("bob", exclude_id=sample_user.id) is not None
        assert UserRepository.get_username_conflict("alice", exclude_id=sample_user.id) is None

    def test_email_conflict_excludes_self(self, sample_user, second_user):
        assert UserRepository.get_email_conflict("bob@example.com", exclude_id=sample_user.id) is not None
        assert UserRepository.get_email_conflict("alice@example.com", exclude_id=sample_user.id) is None

    def test_update(self, sample_user):
        sample_user.username = "alice2"
        UserRepository.update(sample_user)
        assert UserRepository.get_by_id(sample_user.id).username == "alice2"

    def test_delete(self, db, sample_user):
        user_id = sample_user.id
        UserRepository.delete(sample_user)
        assert db.session.get(User, user_id) is None


class TestProjectRepository:
    def test_create(self, sample_user):
        project = ProjectRepository.create("Repo", "desc", sample_user.id)
        assert project.id is not None
        assert project.name == "Repo"
        assert project.owner_id == sample_user.id

    def test_get_by_id(self, sample_project):
        assert ProjectRepository.get_by_id(sample_project.id).name == "TaskFlow"

    def test_get_by_id_missing(self, db):
        assert ProjectRepository.get_by_id(9999) is None

    def test_list_all(self, sample_project):
        assert len(ProjectRepository.list()) == 1

    def test_list_filter_by_owner(self, sample_user, second_user, sample_project):
        assert len(ProjectRepository.list(owner_id=sample_user.id)) == 1
        assert len(ProjectRepository.list(owner_id=second_user.id)) == 0

    def test_name_conflict(self, sample_user, sample_project):
        assert ProjectRepository.get_name_conflict("TaskFlow", sample_user.id) is not None
        assert ProjectRepository.get_name_conflict("Other", sample_user.id) is None

    def test_name_conflict_excludes_self(self, sample_user, sample_project):
        assert ProjectRepository.get_name_conflict(
            "TaskFlow", sample_user.id, exclude_id=sample_project.id
        ) is None

    def test_update(self, sample_project):
        sample_project.name = "Renamed"
        ProjectRepository.update(sample_project)
        assert ProjectRepository.get_by_id(sample_project.id).name == "Renamed"

    def test_delete(self, db, sample_project):
        pid = sample_project.id
        ProjectRepository.delete(sample_project)
        assert db.session.get(Project, pid) is None


class TestTaskRepository:
    def test_create_with_tags(self, sample_project, sample_user):
        task = TaskRepository.create(
            title="Build",
            description="d",
            status=Task.STATUS_TODO,
            priority=Task.PRIORITY_HIGH,
            project_id=sample_project.id,
            assignee_id=sample_user.id,
            tag_names=["bug", "urgent"],
        )
        assert task.id is not None
        assert {t.name for t in task.tags} == {"bug", "urgent"}

    def test_create_minimal(self, sample_project):
        task = TaskRepository.create(
            title="Minimal",
            description="",
            status=Task.STATUS_TODO,
            priority=Task.PRIORITY_MEDIUM,
            project_id=sample_project.id,
        )
        assert task.assignee_id is None
        assert task.tags == []

    def test_get_by_id(self, sample_task):
        assert TaskRepository.get_by_id(sample_task.id).title == "Write tests"

    def test_get_by_id_missing(self, db):
        assert TaskRepository.get_by_id(9999) is None

    def test_list_all(self, sample_task):
        assert len(TaskRepository.list()) == 1

    def test_list_filter_by_status(self, sample_task):
        assert len(TaskRepository.list(status=Task.STATUS_TODO)) == 1
        assert len(TaskRepository.list(status=Task.STATUS_DONE)) == 0

    def test_list_filter_by_priority(self, sample_task):
        assert len(TaskRepository.list(priority=Task.PRIORITY_HIGH)) == 1
        assert len(TaskRepository.list(priority=Task.PRIORITY_LOW)) == 0

    def test_list_filter_by_project(self, sample_task, sample_project):
        assert len(TaskRepository.list(project_id=sample_project.id)) == 1

    def test_list_filter_by_tag(self, sample_project, sample_tag):
        TaskRepository.create(
            title="Tagged",
            description="",
            status=Task.STATUS_TODO,
            priority=Task.PRIORITY_MEDIUM,
            project_id=sample_project.id,
            tag_names=["urgent"],
        )
        assert len(TaskRepository.list(tag="urgent")) == 1
        assert len(TaskRepository.list(tag="nope")) == 0

    def test_set_tags_replaces(self, sample_task):
        TaskRepository.set_tags(sample_task, ["backend", "testing"])
        TaskRepository.update(sample_task)
        assert {t.name for t in sample_task.tags} == {"backend", "testing"}

    def test_update(self, sample_task):
        sample_task.status = Task.STATUS_DONE
        TaskRepository.update(sample_task)
        assert TaskRepository.get_by_id(sample_task.id).status == Task.STATUS_DONE

    def test_delete(self, db, sample_task):
        tid = sample_task.id
        TaskRepository.delete(sample_task)
        assert db.session.get(Task, tid) is None

    def test_count_and_stats(self, sample_task):
        assert TaskRepository.count() == 1
        assert TaskRepository.count_by_status(Task.STATUS_TODO) == 1
        assert TaskRepository.count_by_status(Task.STATUS_DONE) == 0
        assert TaskRepository.count_by_priority(Task.PRIORITY_HIGH) == 1
        assert TaskRepository.count_unassigned() == 0

    def test_count_unassigned(self, sample_project):
        TaskRepository.create(
            title="Lonely",
            description="",
            status=Task.STATUS_TODO,
            priority=Task.PRIORITY_MEDIUM,
            project_id=sample_project.id,
        )
        assert TaskRepository.count_unassigned() == 1


class TestTagRepository:
    def test_create(self, db):
        tag = TagRepository.create("feature")
        assert tag.id is not None
        assert db.session.get(Tag, tag.id) is not None

    def test_get_by_name(self, sample_tag):
        assert TagRepository.get_by_name("urgent") is not None
        assert TagRepository.get_by_name("missing") is None

    def test_get_by_id(self, sample_tag):
        assert TagRepository.get_by_id(sample_tag.id).name == "urgent"

    def test_list_ordered(self, db):
        TagRepository.create("zeta")
        TagRepository.create("alpha")
        names = [t.name for t in TagRepository.list_ordered()]
        assert names == ["alpha", "zeta"]

    def test_get_or_create_existing(self, sample_tag):
        tag = TagRepository.get_or_create("urgent")
        assert tag.id == sample_tag.id

    def test_get_or_create_new(self, db):
        tag = TagRepository.get_or_create("brand-new")
        db.session.commit()
        assert TagRepository.get_by_name("brand-new") is not None
        assert tag.id is not None

    def test_delete(self, db, sample_tag):
        tid = sample_tag.id
        TagRepository.delete(sample_tag)
        assert db.session.get(Tag, tid) is None

    def test_attach_and_detach(self, sample_tag, sample_task):
        TagRepository.attach_to_task(sample_tag, sample_task)
        assert sample_tag in sample_task.tags

        TagRepository.detach_from_task(sample_tag, sample_task)
        assert sample_tag not in sample_task.tags
