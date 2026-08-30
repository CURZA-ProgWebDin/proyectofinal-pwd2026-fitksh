from flask import jsonify, request

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