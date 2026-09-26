from flask import Blueprint

from app.controllers.product_controller import (
    create_product,
    delete_product,
    get_product,
    list_products,
    update_product,
)


product_bp = Blueprint(
    "products",
    __name__,
    url_prefix="/api/products",
)


product_bp.add_url_rule(
    "",
    view_func=list_products,
    methods=["GET"],
)

product_bp.add_url_rule(
    "",
    view_func=create_product,
    methods=["POST"],
)

product_bp.add_url_rule(
    "/<int:product_id>",
    view_func=get_product,
    methods=["GET"],
)

product_bp.add_url_rule(
    "/<int:product_id>",
    view_func=update_product,
    methods=["PUT"],
)

product_bp.add_url_rule(
    "/<int:product_id>",
    view_func=delete_product,
    methods=["DELETE"],
)