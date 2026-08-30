from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity

from app.decorators import roles_required
from app.services.user_service import UserService


@roles_required("ADMINISTRADOR")
def list_users():
    users = UserService.get_all()

    return jsonify(
        {
            "data": [
                user.to_dict()
                for user in users
            ],
            "count": len(users),
        }
    ), 200


@roles_required("ADMINISTRADOR")
def get_user(user_id):
    user = UserService.get_by_id(user_id)

    if user is None:
        return jsonify(
            {
                "error": "El usuario no existe.",
            }
        ), 404

    return jsonify(
        {
            "data": user.to_dict(),
        }
    ), 200


@roles_required("ADMINISTRADOR")
def create_user():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify(
            {
                "error": "Debe enviar un objeto JSON válido.",
            }
        ), 400

    try:
        user = UserService.create(data)
    except ValueError as error:
        return jsonify(
            {
                "error": str(error),
            }
        ), 400
    except FileExistsError as error:
        return jsonify(
            {
                "error": str(error),
            }
        ), 409

    return jsonify(
        {
            "message": "Usuario creado correctamente.",
            "data": user.to_dict(),
        }
    ), 201


@roles_required("ADMINISTRADOR")
def update_user(user_id):
    user = UserService.get_by_id(user_id)

    if user is None:
        return jsonify(
            {
                "error": "El usuario no existe.",
            }
        ), 404

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify(
            {
                "error": "Debe enviar un objeto JSON válido.",
            }
        ), 400

    current_user_id = int(get_jwt_identity())

    try:
        user = UserService.update(
            user,
            data,
            current_user_id,
        )
    except ValueError as error:
        return jsonify(
            {
                "error": str(error),
            }
        ), 400
    except FileExistsError as error:
        return jsonify(
            {
                "error": str(error),
            }
        ), 409
    except PermissionError as error:
        return jsonify(
            {
                "error": str(error),
            }
        ), 409

    return jsonify(
        {
            "message": "Usuario actualizado correctamente.",
            "data": user.to_dict(),
        }
    ), 200


@roles_required("ADMINISTRADOR")
def delete_user(user_id):
    user = UserService.get_by_id(user_id)

    if user is None:
        return jsonify(
            {
                "error": "El usuario no existe.",
            }
        ), 404

    current_user_id = int(get_jwt_identity())

    try:
        user = UserService.deactivate(
            user,
            current_user_id,
        )
    except PermissionError as error:
        return jsonify(
            {
                "error": str(error),
            }
        ), 409

    return jsonify(
        {
            "message": "Usuario desactivado correctamente.",
            "data": user.to_dict(),
        }
    ), 200


@roles_required("ADMINISTRADOR")
def list_roles():
    roles = UserService.get_active_roles()

    return jsonify(
        {
            "data": [
                role.to_dict()
                for role in roles
            ],
            "count": len(roles),
        }
    ), 200