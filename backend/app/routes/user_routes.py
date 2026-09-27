from flask import Blueprint

from app.controllers.user_controller import (
    create_user,
    delete_user,
    get_user,
    list_roles,
    list_users,
    update_user,
)


user_bp = Blueprint(
    "users",
    __name__,
    url_prefix="/api/users",
)

role_bp = Blueprint(
    "roles",
    __name__,
    url_prefix="/api/roles",
)


user_bp.add_url_rule(
    "",
    view_func=list_users,
    methods=["GET"],
)

user_bp.add_url_rule(
    "",
    view_func=create_user,
    methods=["POST"],
)

user_bp.add_url_rule(
    "/<int:user_id>",
    view_func=get_user,
    methods=["GET"],
)

user_bp.add_url_rule(
    "/<int:user_id>",
    view_func=update_user,
    methods=["PUT"],
)

user_bp.add_url_rule(
    "/<int:user_id>",
    view_func=delete_user,
    methods=["DELETE"],
)

role_bp.add_url_rule(
    "",
    view_func=list_roles,
    methods=["GET"],
)