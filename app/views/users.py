from flask import Blueprint, jsonify, request

from app.repositories import UserRepository
from app.schemas.user import user_schema, users_schema

bp = Blueprint("users", __name__, url_prefix="/api/users")


@bp.get("/")
def list_users():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    users, total = UserRepository.list_paginated(page, per_page)

    return jsonify(
        {
            "users": users_schema.dump(users),
            "total": total,
            "page": page,
            "per_page": per_page,
        }
    )


@bp.get("/<int:user_id>")
def get_user(user_id):
    user = UserRepository.get_by_id(user_id)
    if user is None:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"user": user_schema.dump(user)})


@bp.post("/")
def create_user():
    data = request.get_json()
    if not data or "username" not in data or "email" not in data:
        return jsonify({"error": "username and email are required"}), 400

    existing = UserRepository.get_by_username_or_email(
        data["username"], data["email"]
    )
    if existing:
        return jsonify({"error": "Username or email already exists"}), 409

    user = UserRepository.create(data["username"], data["email"])

    return jsonify({"user": user_schema.dump(user)}), 201


@bp.put("/<int:user_id>")
def update_user(user_id):
    user = UserRepository.get_by_id(user_id)
    if user is None:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    if "username" in data:
        conflict = UserRepository.get_username_conflict(
            data["username"], exclude_id=user_id
        )
        if conflict:
            return jsonify({"error": "Username already taken"}), 409
        user.username = data["username"]

    if "email" in data:
        conflict = UserRepository.get_email_conflict(
            data["email"], exclude_id=user_id
        )
        if conflict:
            return jsonify({"error": "Email already taken"}), 409
        user.email = data["email"]

    UserRepository.update(user)
    return jsonify({"user": user_schema.dump(user)})


@bp.delete("/<int:user_id>")
def delete_user(user_id):
    user = UserRepository.get_by_id(user_id)
    if user is None:
        return jsonify({"error": "User not found"}), 404

    # Check if user owns projects or has assigned tasks
    if user.owned_projects:
        return jsonify({"error": "Cannot delete user who owns projects"}), 409
    if user.assigned_tasks:
        return jsonify({"error": "Cannot delete user with assigned tasks"}), 409

    UserRepository.delete(user)
    return jsonify({"message": "User deleted"}), 200
