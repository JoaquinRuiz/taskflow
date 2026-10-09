import json


class TestUsers:
    def test_create_user(self, client):
        resp = client.post("/api/users/", json={"username": "charlie", "email": "charlie@example.com"})
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["user"]["username"] == "charlie"
        assert data["user"]["email"] == "charlie@example.com"
        assert "id" in data["user"]

    def test_create_user_missing_fields(self, client):
        resp = client.post("/api/users/", json={"username": "charlie"})
        assert resp.status_code == 400

    def test_create_user_duplicate_username(self, client, sample_user):
        resp = client.post("/api/users/", json={"username": "alice", "email": "other@example.com"})
        assert resp.status_code == 409

    def test_create_user_duplicate_email(self, client, sample_user):
        resp = client.post("/api/users/", json={"username": "other", "email": "alice@example.com"})
        assert resp.status_code == 409

    def test_get_user(self, client, sample_user):
        resp = client.get(f"/api/users/{sample_user.id}")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["user"]["username"] == "alice"

    def test_get_user_not_found(self, client):
        resp = client.get("/api/users/9999")
        assert resp.status_code == 404

    def test_list_users(self, client, sample_user, second_user):
        resp = client.get("/api/users/")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["total"] == 2
        assert len(data["users"]) == 2

    def test_update_user(self, client, sample_user):
        resp = client.put(
            f"/api/users/{sample_user.id}",
            json={"username": "alice_updated"},
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["user"]["username"] == "alice_updated"

    def test_update_user_conflict(self, client, sample_user, second_user):
        resp = client.put(
            f"/api/users/{sample_user.id}",
            json={"username": "bob"},
        )
        assert resp.status_code == 409

    def test_delete_user(self, client, second_user):
        resp = client.delete(f"/api/users/{second_user.id}")
        assert resp.status_code == 200

    def test_delete_user_with_projects(self, client, sample_user, sample_project):
        resp = client.delete(f"/api/users/{sample_user.id}")
        assert resp.status_code == 409

    def test_list_users_pagination(self, client, sample_user, second_user):
        resp = client.get("/api/users/?page=1&per_page=1")
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data["users"]) == 1
        assert data["total"] == 2
