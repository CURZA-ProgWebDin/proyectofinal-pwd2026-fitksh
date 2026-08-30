from flask import Blueprint

from app.controllers.auth_controller import register


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