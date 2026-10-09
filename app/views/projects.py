from flask import Blueprint, jsonify, request

from app.repositories import ProjectRepository, UserRepository
from app.schemas.project import project_schema

bp = Blueprint("projects", __name__, url_prefix="/api/projects")


def _serialize_project(project):
    data = project_schema.dump(project)
    data["owner_username"] = project.owner.username
    data["task_count"] = len(project.tasks)
    return data


@bp.get("/")
def list_projects():
    owner_id = request.args.get("owner_id", type=int)

    projects = ProjectRepository.list(owner_id=owner_id)
    result = [_serialize_project(p) for p in projects]
    return jsonify({"projects": result})


@bp.get("/<int:project_id>")
def get_project(project_id):
    project = ProjectRepository.get_by_id(project_id)
    if project is None:
        return jsonify({"error": "Project not found"}), 404
    return jsonify({"project": _serialize_project(project)})


@bp.post("/")
def create_project():
    data = request.get_json()
    if not data or "name" not in data or "owner_id" not in data:
        return jsonify({"error": "name and owner_id are required"}), 400

    owner = UserRepository.get_by_id(data["owner_id"])
    if owner is None:
        return jsonify({"error": "Owner not found"}), 404

    # Check for duplicate name for same owner
    existing = ProjectRepository.get_name_conflict(
        data["name"], data["owner_id"]
    )
    if existing:
        return jsonify({"error": "Project with this name already exists for this owner"}), 409

    project = ProjectRepository.create(
        name=data["name"],
        description=data.get("description", ""),
        owner_id=data["owner_id"],
    )

    return jsonify({"project": _serialize_project(project)}), 201


@bp.put("/<int:project_id>")
def update_project(project_id):
    project = ProjectRepository.get_by_id(project_id)
    if project is None:
        return jsonify({"error": "Project not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    if "name" in data:
        conflict = ProjectRepository.get_name_conflict(
            data["name"], project.owner_id, exclude_id=project_id
        )
        if conflict:
            return jsonify({"error": "Project name already taken"}), 409
        project.name = data["name"]

    if "description" in data:
        project.description = data["description"]

    ProjectRepository.update(project)
    return jsonify({"project": _serialize_project(project)})


@bp.delete("/<int:project_id>")
def delete_project(project_id):
    project = ProjectRepository.get_by_id(project_id)
    if project is None:
        return jsonify({"error": "Project not found"}), 404

    ProjectRepository.delete(project)
    return jsonify({"message": "Project deleted"}), 200
