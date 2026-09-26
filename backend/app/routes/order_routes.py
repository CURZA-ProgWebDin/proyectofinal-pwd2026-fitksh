from flask import Blueprint

from app.controllers.order_controller import (
    cancel_order,
    create_order,
    get_order,
    list_orders,
    list_order_statuses,
    update_order,
)


order_bp = Blueprint(
    "orders",
    __name__,
    url_prefix="/api/orders",
)

order_status_bp = Blueprint(
    "order_statuses",
    __name__,
    url_prefix="/api/order-statuses",
)


order_bp.add_url_rule(
    "",
    view_func=list_orders,
    methods=["GET"],
)

order_bp.add_url_rule(
    "",
    view_func=create_order,
    methods=["POST"],
)

order_bp.add_url_rule(
    "/<int:order_id>",
    view_func=get_order,
    methods=["GET"],
)

order_bp.add_url_rule(
    "/<int:order_id>",
    view_func=update_order,
    methods=["PUT"],
)

order_bp.add_url_rule(
    "/<int:order_id>",
    view_func=cancel_order,
    methods=["DELETE"],
)

order_status_bp.add_url_rule(
    "",
    view_func=list_order_statuses,
    methods=["GET"],
)