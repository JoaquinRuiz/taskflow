from flask import Blueprint, jsonify, request

from app.models.task import Task
from app.repositories import TaskRepository, ProjectRepository, UserRepository

bp = Blueprint("tasks", __name__, url_prefix="/api/tasks")


def _serialize_task(task):
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "priority": task.priority,
        "project_id": task.project_id,
        "project_name": task.project.name,
        "assignee_id": task.assignee_id,
        "assignee_username": task.assignee.username if task.assignee else None,
        "tags": [t.name for t in task.tags],
        "created_at": task.created_at.isoformat() if task.created_at else None,
        "updated_at": task.updated_at.isoformat() if task.updated_at else None,
    }


@bp.get("/")
def list_tasks():
    project_id = request.args.get("project_id", type=int)
    assignee_id = request.args.get("assignee_id", type=int)
    status = request.args.get("status")
    priority = request.args.get("priority")
    tag = request.args.get("tag")

    if status and status not in Task.VALID_STATUSES:
        return jsonify({"error": f"Invalid status. Must be one of: {Task.VALID_STATUSES}"}), 400
    if priority and priority not in Task.VALID_PRIORITIES:
        return jsonify({"error": f"Invalid priority. Must be one of: {Task.VALID_PRIORITIES}"}), 400

    tasks = TaskRepository.list(
        project_id=project_id,
        assignee_id=assignee_id,
        status=status,
        priority=priority,
        tag=tag,
    )
    return jsonify({"tasks": [_serialize_task(t) for t in tasks]})


@bp.get("/<int:task_id>")
def get_task(task_id):
    task = TaskRepository.get_by_id(task_id)
    if task is None:
        return jsonify({"error": "Task not found"}), 404
    return jsonify({"task": _serialize_task(task)})


@bp.post("/")
def create_task():
    data = request.get_json()
    if not data or "title" not in data or "project_id" not in data:
        return jsonify({"error": "title and project_id are required"}), 400

    project = ProjectRepository.get_by_id(data["project_id"])
    if project is None:
        return jsonify({"error": "Project not found"}), 404

    status = data.get("status", Task.STATUS_TODO)
    if status not in Task.VALID_STATUSES:
        return jsonify({"error": f"Invalid status. Must be one of: {Task.VALID_STATUSES}"}), 400

    priority = data.get("priority", Task.PRIORITY_MEDIUM)
    if priority not in Task.VALID_PRIORITIES:
        return jsonify({"error": f"Invalid priority. Must be one of: {Task.VALID_PRIORITIES}"}), 400

    assignee_id = data.get("assignee_id")
    if assignee_id is not None:
        assignee = UserRepository.get_by_id(assignee_id)
        if assignee is None:
            return jsonify({"error": "Assignee not found"}), 404

    task = TaskRepository.create(
        title=data["title"],
        description=data.get("description", ""),
        status=status,
        priority=priority,
        project_id=data["project_id"],
        assignee_id=assignee_id,
        tag_names=data.get("tags", []),
    )

    return jsonify({"task": _serialize_task(task)}), 201


@bp.put("/<int:task_id>")
def update_task(task_id):
    task = TaskRepository.get_by_id(task_id)
    if task is None:
        return jsonify({"error": "Task not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    if "title" in data:
        task.title = data["title"]
    if "description" in data:
        task.description = data["description"]

    if "status" in data:
        if data["status"] not in Task.VALID_STATUSES:
            return jsonify({"error": f"Invalid status. Must be one of: {Task.VALID_STATUSES}"}), 400
        task.status = data["status"]

    if "priority" in data:
        if data["priority"] not in Task.VALID_PRIORITIES:
            return jsonify({"error": f"Invalid priority. Must be one of: {Task.VALID_PRIORITIES}"}), 400
        task.priority = data["priority"]

    if "assignee_id" in data:
        if data["assignee_id"] is not None:
            assignee = UserRepository.get_by_id(data["assignee_id"])
            if assignee is None:
                return jsonify({"error": "Assignee not found"}), 404
        task.assignee_id = data["assignee_id"]

    if "tags" in data:
        TaskRepository.set_tags(task, data["tags"])

    TaskRepository.update(task)
    return jsonify({"task": _serialize_task(task)})


@bp.delete("/<int:task_id>")
def delete_task(task_id):
    task = TaskRepository.get_by_id(task_id)
    if task is None:
        return jsonify({"error": "Task not found"}), 404

    TaskRepository.delete(task)
    return jsonify({"message": "Task deleted"}), 200


@bp.post("/<int:task_id>/assign")
def assign_task(task_id):
    task = TaskRepository.get_by_id(task_id)
    if task is None:
        return jsonify({"error": "Task not found"}), 404

    data = request.get_json()
    if not data or "assignee_id" not in data:
        return jsonify({"error": "assignee_id is required"}), 400

    assignee = UserRepository.get_by_id(data["assignee_id"])
    if assignee is None:
        return jsonify({"error": "Assignee not found"}), 404

    task.assignee_id = data["assignee_id"]
    TaskRepository.update(task)
    return jsonify({"task": _serialize_task(task)})


@bp.post("/<int:task_id>/unassign")
def unassign_task(task_id):
    task = TaskRepository.get_by_id(task_id)
    if task is None:
        return jsonify({"error": "Task not found"}), 404

    task.assignee_id = None
    TaskRepository.update(task)
    return jsonify({"task": _serialize_task(task)})


@bp.get("/stats")
def task_stats():
    """Get task statistics grouped by status and priority."""
    project_id = request.args.get("project_id", type=int)

    total = TaskRepository.count(project_id)
    by_status = {
        status: TaskRepository.count_by_status(status, project_id)
        for status in Task.VALID_STATUSES
    }
    by_priority = {
        priority: TaskRepository.count_by_priority(priority, project_id)
        for priority in Task.VALID_PRIORITIES
    }
    unassigned = TaskRepository.count_unassigned(project_id)

    return jsonify({
        "total": total,
        "by_status": by_status,
        "by_priority": by_priority,
        "unassigned": unassigned,
    })
