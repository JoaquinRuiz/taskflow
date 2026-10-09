class TestTasks:
    def test_create_task(self, client, sample_project, sample_user):
        resp = client.post("/api/tasks/", json={
            "title": "Fix bug",
            "description": "Fix the login bug",
            "project_id": sample_project.id,
            "assignee_id": sample_user.id,
            "priority": "high",
            "tags": ["bug", "urgent"],
        })
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["task"]["title"] == "Fix bug"
        assert data["task"]["assignee_username"] == "alice"
        assert data["task"]["status"] == "todo"
        assert set(data["task"]["tags"]) == {"bug", "urgent"}

    def test_create_task_minimal(self, client, sample_project):
        resp = client.post("/api/tasks/", json={
            "title": "Simple task",
            "project_id": sample_project.id,
        })
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["task"]["status"] == "todo"
        assert data["task"]["priority"] == "medium"
        assert data["task"]["assignee_id"] is None

    def test_create_task_missing_fields(self, client):
        resp = client.post("/api/tasks/", json={"title": "No project"})
        assert resp.status_code == 400

    def test_create_task_invalid_project(self, client):
        resp = client.post("/api/tasks/", json={"title": "X", "project_id": 9999})
        assert resp.status_code == 404

    def test_create_task_invalid_status(self, client, sample_project):
        resp = client.post("/api/tasks/", json={
            "title": "X",
            "project_id": sample_project.id,
            "status": "invalid",
        })
        assert resp.status_code == 400

    def test_create_task_invalid_assignee(self, client, sample_project):
        resp = client.post("/api/tasks/", json={
            "title": "X",
            "project_id": sample_project.id,
            "assignee_id": 9999,
        })
        assert resp.status_code == 404

    def test_get_task(self, client, sample_task):
        resp = client.get(f"/api/tasks/{sample_task.id}")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["task"]["title"] == "Write tests"
        assert data["task"]["project_name"] == "TaskFlow"

    def test_get_task_not_found(self, client):
        resp = client.get("/api/tasks/9999")
        assert resp.status_code == 404

    def test_list_tasks(self, client, sample_task):
        resp = client.get("/api/tasks/")
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data["tasks"]) == 1

    def test_list_tasks_filter_by_status(self, client, sample_task):
        resp = client.get("/api/tasks/?status=todo")
        data = resp.get_json()
        assert len(data["tasks"]) == 1

        resp = client.get("/api/tasks/?status=done")
        data = resp.get_json()
        assert len(data["tasks"]) == 0

    def test_list_tasks_filter_by_priority(self, client, sample_task):
        resp = client.get("/api/tasks/?priority=high")
        data = resp.get_json()
        assert len(data["tasks"]) == 1

    def test_list_tasks_filter_invalid_status(self, client):
        resp = client.get("/api/tasks/?status=invalid")
        assert resp.status_code == 400

    def test_list_tasks_filter_by_project(self, client, sample_task, sample_project):
        resp = client.get(f"/api/tasks/?project_id={sample_project.id}")
        data = resp.get_json()
        assert len(data["tasks"]) == 1

    def test_list_tasks_filter_by_tag(self, client, sample_project, sample_user, sample_tag, db):
        from app.models.task import Task
        task = Task(title="Tagged", project_id=sample_project.id, assignee_id=sample_user.id)
        task.tags.append(sample_tag)
        db.session.add(task)
        db.session.commit()

        resp = client.get("/api/tasks/?tag=urgent")
        data = resp.get_json()
        assert len(data["tasks"]) == 1
        assert data["tasks"][0]["title"] == "Tagged"

    def test_update_task(self, client, sample_task):
        resp = client.put(f"/api/tasks/{sample_task.id}", json={
            "title": "Write better tests",
            "status": "in_progress",
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["task"]["title"] == "Write better tests"
        assert data["task"]["status"] == "in_progress"

    def test_update_task_tags(self, client, sample_task):
        resp = client.put(f"/api/tasks/{sample_task.id}", json={
            "tags": ["backend", "testing"],
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert set(data["task"]["tags"]) == {"backend", "testing"}

    def test_delete_task(self, client, sample_task):
        resp = client.delete(f"/api/tasks/{sample_task.id}")
        assert resp.status_code == 200

    def test_assign_task(self, client, sample_task, second_user):
        resp = client.post(f"/api/tasks/{sample_task.id}/assign", json={
            "assignee_id": second_user.id,
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["task"]["assignee_username"] == "bob"

    def test_assign_task_invalid_user(self, client, sample_task):
        resp = client.post(f"/api/tasks/{sample_task.id}/assign", json={
            "assignee_id": 9999,
        })
        assert resp.status_code == 404

    def test_unassign_task(self, client, sample_task):
        resp = client.post(f"/api/tasks/{sample_task.id}/unassign")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["task"]["assignee_id"] is None

    def test_task_stats(self, client, sample_task):
        resp = client.get("/api/tasks/stats")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["total"] == 1
        assert data["by_status"]["todo"] == 1
        assert data["by_priority"]["high"] == 1
        assert data["unassigned"] == 0

    def test_task_stats_by_project(self, client, sample_task, sample_project):
        resp = client.get(f"/api/tasks/stats?project_id={sample_project.id}")
        data = resp.get_json()
        assert data["total"] == 1
