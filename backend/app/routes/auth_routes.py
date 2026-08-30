from flask import Blueprint

from app.controllers.auth_controller import (
    get_current_user,
    login,
    register,
)


auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/api/auth",
)


auth_bp.add_url_rule(
    "/register",
    view_func=register,
    methods=["POST"],
)

auth_bp.add_url_rule(
    "/login",
    view_func=login,
    methods=["POST"],
)

auth_bp.add_url_rule(
    "/me",
    view_func=get_current_user,
    methods=["GET"],
)