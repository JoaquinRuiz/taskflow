from flask import Blueprint, jsonify, request

from app.repositories import TagRepository, TaskRepository

bp = Blueprint("tags", __name__, url_prefix="/api/tags")


@bp.get("/")
def list_tags():
    tags = TagRepository.list_ordered()
    result = []
    for tag in tags:
        result.append({
            "id": tag.id,
            "name": tag.name,
            "task_count": len(tag.tasks),
        })
    return jsonify({"tags": result})


@bp.post("/")
def create_tag():
    data = request.get_json()
    if not data or "name" not in data:
        return jsonify({"error": "name is required"}), 400

    existing = TagRepository.get_by_name(data["name"])
    if existing:
        return jsonify({"error": "Tag already exists"}), 409

    tag = TagRepository.create(data["name"])

    return jsonify({"tag": {"id": tag.id, "name": tag.name, "task_count": 0}}), 201


@bp.delete("/<int:tag_id>")
def delete_tag(tag_id):
    tag = TagRepository.get_by_id(tag_id)
    if tag is None:
        return jsonify({"error": "Tag not found"}), 404

    TagRepository.delete(tag)
    return jsonify({"message": "Tag deleted"}), 200


@bp.post("/<int:tag_id>/attach/<int:task_id>")
def attach_tag(tag_id, task_id):
    tag = TagRepository.get_by_id(tag_id)
    if tag is None:
        return jsonify({"error": "Tag not found"}), 404

    task = TaskRepository.get_by_id(task_id)
    if task is None:
        return jsonify({"error": "Task not found"}), 404

    if tag in task.tags:
        return jsonify({"error": "Tag already attached to this task"}), 409

    TagRepository.attach_to_task(tag, task)
    return jsonify({"message": f"Tag '{tag.name}' attached to task '{task.title}'"}), 200


@bp.post("/<int:tag_id>/detach/<int:task_id>")
def detach_tag(tag_id, task_id):
    tag = TagRepository.get_by_id(tag_id)
    if tag is None:
        return jsonify({"error": "Tag not found"}), 404

    task = TaskRepository.get_by_id(task_id)
    if task is None:
        return jsonify({"error": "Task not found"}), 404

    if tag not in task.tags:
        return jsonify({"error": "Tag is not attached to this task"}), 404

    TagRepository.detach_from_task(tag, task)
    return jsonify({"message": f"Tag '{tag.name}' detached from task '{task.title}'"}), 200
