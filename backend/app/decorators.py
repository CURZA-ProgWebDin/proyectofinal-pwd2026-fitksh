from functools import wraps

from flask import jsonify
from flask_jwt_extended import (
    get_jwt_identity,
    verify_jwt_in_request,
)

from app.services.auth_service import AuthService


def roles_required(*allowed_roles):
    normalized_roles = {
        role.upper()
        for role in allowed_roles
    }

    def decorator(view_function):
        @wraps(view_function)
        def wrapped_view(*args, **kwargs):
            verify_jwt_in_request()

            identity = get_jwt_identity()

            try:
                user = AuthService.get_authenticated_user(
                    identity
                )
            except PermissionError as error:
                return jsonify(
                    {
                        "error": str(error),
                    }
                ), 403

            current_role = user.role.name.upper()

            if current_role not in normalized_roles:
                return jsonify(
                    {
                        "error": (
                            "No tiene permisos para realizar "
                            "esta operación."
                        ),
                    }
                ), 403

            return view_function(*args, **kwargs)

        return wrapped_view

    return decorator