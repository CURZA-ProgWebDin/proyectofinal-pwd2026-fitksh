from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity

from app.decorators import roles_required
from app.services.cart_service import CartService


def _get_current_user_id():
    return int(get_jwt_identity())


@roles_required("CLIENTE")
def get_cart():
    cart = CartService.get_by_user_id(
        _get_current_user_id()
    )

    return jsonify(
        {
            "data": CartService.serialize(cart),
        }
    ), 200


@roles_required("CLIENTE")
def add_cart_item():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify(
            {
                "error": "Debe enviar un objeto JSON válido.",
            }
        ), 400

    try:
        cart, created = CartService.add_item(
            _get_current_user_id(),
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

    message = (
        "Producto agregado al carrito."
        if created
        else "Cantidad del producto actualizada."
    )

    status_code = 201 if created else 200

    return jsonify(
        {
            "message": message,
            "data": CartService.serialize(cart),
        }
    ), status_code


@roles_required("CLIENTE")
def update_cart_item(item_id):
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify(
            {
                "error": "Debe enviar un objeto JSON válido.",
            }
        ), 400

    try:
        cart = CartService.update_item(
            _get_current_user_id(),
            item_id,
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
            "message": "Cantidad actualizada correctamente.",
            "data": CartService.serialize(cart),
        }
    ), 200


@roles_required("CLIENTE")
def delete_cart_item(item_id):
    try:
        cart = CartService.remove_item(
            _get_current_user_id(),
            item_id,
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
            "message": "Producto quitado del carrito.",
            "data": CartService.serialize(cart),
        }
    ), 200


@roles_required("CLIENTE")
def clear_cart():
    try:
        cart = CartService.clear(
            _get_current_user_id()
        )
    except ValueError as error:
        return jsonify(
            {
                "error": str(error),
            }
        ), 400

    return jsonify(
        {
            "message": "Carrito vaciado correctamente.",
            "data": CartService.serialize(cart),
        }
    ), 200