from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity

from app.decorators import roles_required
from app.services.auth_service import AuthService
from app.services.order_service import OrderService


def _get_current_user():
    return AuthService.get_authenticated_user(
        get_jwt_identity()
    )


@roles_required("CLIENTE", "ADMINISTRADOR")
def list_orders():
    user = _get_current_user()

    orders = OrderService.list_for_user(user)

    return jsonify(
        {
            "data": [
                OrderService.serialize(order)
                for order in orders
            ],
            "count": len(orders),
        }
    ), 200


@roles_required("CLIENTE", "ADMINISTRADOR")
def get_order(order_id):
    user = _get_current_user()

    order = OrderService.get_accessible_by_id(
        order_id,
        user,
    )

    if order is None:
        return jsonify(
            {
                "error": "El pedido no existe.",
            }
        ), 404

    return jsonify(
        {
            "data": OrderService.serialize(order),
        }
    ), 200


@roles_required("CLIENTE")
def create_order():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify(
            {
                "error": "Debe enviar un objeto JSON válido.",
            }
        ), 400

    user = _get_current_user()

    try:
        order = OrderService.create_from_cart(
            user.id,
            data,
        )
    except LookupError as error:
        return jsonify(
            {
                "error": str(error),
            }
        ), 404
    except ValueError as error:
        return jsonify(
            {
                "error": str(error),
            }
        ), 400
    except RuntimeError as error:
        return jsonify(
            {
                "error": str(error),
            }
        ), 500

    return jsonify(
        {
            "message": "Pedido creado correctamente.",
            "data": OrderService.serialize(order),
        }
    ), 201


@roles_required("ADMINISTRADOR")
def update_order(order_id):
    user = _get_current_user()

    order = OrderService.get_accessible_by_id(
        order_id,
        user,
    )

    if order is None:
        return jsonify(
            {
                "error": "El pedido no existe.",
            }
        ), 404

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify(
            {
                "error": "Debe enviar un objeto JSON válido.",
            }
        ), 400

    try:
        order = OrderService.update_status(
            order,
            data,
        )
    except LookupError as error:
        return jsonify(
            {
                "error": str(error),
            }
        ), 404
    except ValueError as error:
        return jsonify(
            {
                "error": str(error),
            }
        ), 400

    return jsonify(
        {
            "message": (
                "Estado del pedido actualizado correctamente."
            ),
            "data": OrderService.serialize(order),
        }
    ), 200


@roles_required("CLIENTE")
def cancel_order(order_id):
    user = _get_current_user()

    order = OrderService.get_accessible_by_id(
        order_id,
        user,
    )

    if order is None:
        return jsonify(
            {
                "error": "El pedido no existe.",
            }
        ), 404

    try:
        order = OrderService.cancel_pending_order(
            order
        )
    except ValueError as error:
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
            "message": "Pedido cancelado correctamente.",
            "data": OrderService.serialize(order),
        }
    ), 200


@roles_required("ADMINISTRADOR")
def list_order_statuses():
    statuses = OrderService.list_statuses()

    return jsonify(
        {
            "data": [
                OrderService.serialize_status(status)
                for status in statuses
            ],
            "count": len(statuses),
        }
    ), 200