class TestTags:
    def test_create_tag(self, client):
        resp = client.post("/api/tags/", json={"name": "feature"})
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["tag"]["name"] == "feature"
        assert data["tag"]["task_count"] == 0

    def test_create_tag_duplicate(self, client, sample_tag):
        resp = client.post("/api/tags/", json={"name": "urgent"})
        assert resp.status_code == 409

    def test_create_tag_missing_name(self, client):
        resp = client.post("/api/tags/", json={})
        assert resp.status_code == 400

    def test_list_tags(self, client, sample_tag):
        resp = client.get("/api/tags/")
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data["tags"]) == 1
        assert data["tags"][0]["name"] == "urgent"

    def test_delete_tag(self, client, sample_tag):
        resp = client.delete(f"/api/tags/{sample_tag.id}")
        assert resp.status_code == 200

    def test_delete_tag_not_found(self, client):
        resp = client.delete("/api/tags/9999")
        assert resp.status_code == 404

    def test_attach_tag_to_task(self, client, sample_tag, sample_task):
        resp = client.post(f"/api/tags/{sample_tag.id}/attach/{sample_task.id}")
        assert resp.status_code == 200

        # Verify tag appears on task
        resp = client.get(f"/api/tasks/{sample_task.id}")
        data = resp.get_json()
        assert "urgent" in data["task"]["tags"]

    def test_attach_tag_duplicate(self, client, sample_tag, sample_task):
        client.post(f"/api/tags/{sample_tag.id}/attach/{sample_task.id}")
        resp = client.post(f"/api/tags/{sample_tag.id}/attach/{sample_task.id}")
        assert resp.status_code == 409

    def test_attach_tag_not_found(self, client, sample_task):
        resp = client.post(f"/api/tags/9999/attach/{sample_task.id}")
        assert resp.status_code == 404

    def test_detach_tag(self, client, sample_tag, sample_task):
        client.post(f"/api/tags/{sample_tag.id}/attach/{sample_task.id}")
        resp = client.post(f"/api/tags/{sample_tag.id}/detach/{sample_task.id}")
        assert resp.status_code == 200

    def test_detach_tag_not_attached(self, client, sample_tag, sample_task):
        resp = client.post(f"/api/tags/{sample_tag.id}/detach/{sample_task.id}")
        assert resp.status_code == 404

    def test_tag_task_count(self, client, sample_tag, sample_task):
        client.post(f"/api/tags/{sample_tag.id}/attach/{sample_task.id}")
        resp = client.get("/api/tags/")
        data = resp.get_json()
        tag_data = next(t for t in data["tags"] if t["name"] == "urgent")
        assert tag_data["task_count"] == 1
