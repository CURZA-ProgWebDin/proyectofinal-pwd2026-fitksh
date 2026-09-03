from flask import jsonify, request

from flask_jwt_extended import (
    get_jwt,
    get_jwt_identity,
    jwt_required,
)

from app.services.auth_service import AuthService


def register():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify(
            {
                "error": "Debe enviar un objeto JSON válido.",
            }
        ), 400

    try:
        user = AuthService.register(data)
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
    except RuntimeError as error:
        return jsonify(
            {
                "error": str(error),
            }
        ), 500

    return jsonify(
        {
            "message": "Usuario registrado correctamente.",
            "data": user.to_dict(),
        }
    ), 201


def login():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify(
            {
                "error": "Debe enviar un objeto JSON válido.",
            }
        ), 400

    try:
        user, access_token, refresh_token = AuthService.login(data)
    except ValueError as error:
        return jsonify(
            {
                "error": str(error),
            }
        ), 400
    except PermissionError as error:
        return jsonify(
            {
                "error": str(error),
            }
        ), 401

    return jsonify(
        {
            "message": "Inicio de sesión correcto.",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "user": user.to_dict(),
        }
    ), 200


@jwt_required()
def get_current_user():
    identity = get_jwt_identity()

    try:
        user = AuthService.get_authenticated_user(identity)
    except PermissionError as error:
        return jsonify(
            {
                "error": str(error),
            }
        ), 403

    return jsonify(
        {
            "data": user.to_dict(),
        }
    ), 200
    
@jwt_required(refresh=True)
def refresh_access_token():
    identity = get_jwt_identity()
    token_identifier = get_jwt()["jti"]

    try:
        access_token = AuthService.refresh_access_token(
            identity,
            token_identifier,
        )
    except PermissionError as error:
        return jsonify(
            {
                "error": str(error),
            }
        ), 401

    return jsonify(
        {
            "message": "Access token renovado correctamente.",
            "access_token": access_token,
            "token_type": "Bearer",
        }
    ), 200
    
@jwt_required(refresh=True)
def logout():
    identity = get_jwt_identity()
    token_identifier = get_jwt()["jti"]

    try:
        AuthService.revoke_refresh_token(
            identity,
            token_identifier,
        )
    except PermissionError as error:
        return jsonify(
            {
                "error": str(error),
            }
        ), 401

    return jsonify(
        {
            "message": "Sesión cerrada correctamente.",
        }
    ), 200