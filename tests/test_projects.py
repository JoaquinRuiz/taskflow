class TestProjects:
    def test_create_project(self, client, sample_user):
        resp = client.post("/api/projects/", json={
            "name": "New Project",
            "description": "A brand new project",
            "owner_id": sample_user.id,
        })
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["project"]["name"] == "New Project"
        assert data["project"]["owner_username"] == "alice"
        assert data["project"]["task_count"] == 0

    def test_create_project_missing_fields(self, client):
        resp = client.post("/api/projects/", json={"name": "No owner"})
        assert resp.status_code == 400

    def test_create_project_invalid_owner(self, client):
        resp = client.post("/api/projects/", json={"name": "X", "owner_id": 9999})
        assert resp.status_code == 404

    def test_create_project_duplicate_name(self, client, sample_user, sample_project):
        resp = client.post("/api/projects/", json={
            "name": "TaskFlow",
            "owner_id": sample_user.id,
        })
        assert resp.status_code == 409

    def test_get_project(self, client, sample_project):
        resp = client.get(f"/api/projects/{sample_project.id}")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["project"]["name"] == "TaskFlow"

    def test_get_project_not_found(self, client):
        resp = client.get("/api/projects/9999")
        assert resp.status_code == 404

    def test_list_projects(self, client, sample_project):
        resp = client.get("/api/projects/")
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data["projects"]) == 1

    def test_list_projects_filter_by_owner(self, client, sample_user, second_user, sample_project):
        resp = client.get(f"/api/projects/?owner_id={second_user.id}")
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data["projects"]) == 0

    def test_update_project(self, client, sample_project):
        resp = client.put(
            f"/api/projects/{sample_project.id}",
            json={"name": "TaskFlow v2", "description": "Updated"},
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["project"]["name"] == "TaskFlow v2"

    def test_delete_project(self, client, sample_project):
        resp = client.delete(f"/api/projects/{sample_project.id}")
        assert resp.status_code == 200

    def test_project_task_count(self, client, sample_project, sample_task):
        resp = client.get(f"/api/projects/{sample_project.id}")
        data = resp.get_json()
        assert data["project"]["task_count"] == 1
