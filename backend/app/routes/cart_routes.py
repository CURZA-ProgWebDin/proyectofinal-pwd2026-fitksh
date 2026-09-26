from flask import Blueprint

from app.controllers.cart_controller import (
    add_cart_item,
    clear_cart,
    delete_cart_item,
    get_cart,
    update_cart_item,
)


cart_bp = Blueprint(
    "cart",
    __name__,
    url_prefix="/api/cart",
)


cart_bp.add_url_rule(
    "",
    view_func=get_cart,
    methods=["GET"],
)

cart_bp.add_url_rule(
    "",
    view_func=clear_cart,
    methods=["DELETE"],
)

cart_bp.add_url_rule(
    "/items",
    view_func=add_cart_item,
    methods=["POST"],
)

cart_bp.add_url_rule(
    "/items/<int:item_id>",
    view_func=update_cart_item,
    methods=["PUT"],
)

cart_bp.add_url_rule(
    "/items/<int:item_id>",
    view_func=delete_cart_item,
    methods=["DELETE"],
)