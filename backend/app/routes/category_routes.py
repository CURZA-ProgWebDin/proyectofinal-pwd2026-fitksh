from flask import Blueprint

from app.controllers.category_controller import (
    create_category,
    delete_category,
    get_category,
    list_categories,
    update_category,
)


category_bp = Blueprint(
    "categories",
    __name__,
    url_prefix="/api/categories",
)


category_bp.add_url_rule(
    "",
    view_func=list_categories,
    methods=["GET"],
)

category_bp.add_url_rule(
    "",
    view_func=create_category,
    methods=["POST"],
)

category_bp.add_url_rule(
    "/<int:category_id>",
    view_func=get_category,
    methods=["GET"],
)

category_bp.add_url_rule(
    "/<int:category_id>",
    view_func=update_category,
    methods=["PUT"],
)

category_bp.add_url_rule(
    "/<int:category_id>",
    view_func=delete_category,
    methods=["DELETE"],
)