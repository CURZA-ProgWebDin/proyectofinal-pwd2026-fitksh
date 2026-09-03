from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models.cart import Cart
from app.models.order import Order
from app.models.order_detail import OrderDetail
from app.models.order_status import OrderStatus


class OrderService:
    ALLOWED_TRANSITIONS = {
        "PENDIENTE": {
            "CONFIRMADO",
            "CANCELADO",
        },
        "CONFIRMADO": {
            "EN_PREPARACION",
            "CANCELADO",
        },
        "EN_PREPARACION": {
            "LISTO",
            "CANCELADO",
        },
        "LISTO": {
            "ENTREGADO",
        },
        "ENTREGADO": set(),
        "CANCELADO": set(),
    }

    @staticmethod
    def list_for_user(user):
        query = Order.query

        if user.role.name.upper() != "ADMINISTRADOR":
            query = query.filter_by(user_id=user.id)

        return query.order_by(
            Order.ordered_at.desc()
        ).all()

    @staticmethod
    def get_accessible_by_id(order_id, user):
        order = db.session.get(Order, order_id)

        if order is None:
            return None

        is_admin = (
            user.role.name.upper() == "ADMINISTRADOR"
        )

        if is_admin or order.user_id == user.id:
            return order

        return None

    @staticmethod
    def list_statuses():
        return OrderStatus.query.order_by(
            OrderStatus.id
        ).all()

    @staticmethod
    def create_from_cart(user_id, data):
        notes = OrderService._validate_notes(
            data.get("notes")
        )

        cart = Cart.query.filter_by(
            user_id=user_id
        ).first()

        if cart is None or not cart.items:
            raise ValueError(
                "No se puede crear un pedido con el carrito vacío."
            )

        pending_status = (
            OrderService._get_status_by_name(
                "PENDIENTE"
            )
        )

        cart_items = list(cart.items)

        for item in cart_items:
            product = item.product

            if product is None:
                raise LookupError(
                    "Uno de los productos del carrito ya no existe."
                )

            if not product.active:
                raise ValueError(
                    (
                        f"El producto '{product.name}' "
                        "ya no está disponible."
                    )
                )

            if item.quantity > product.stock:
                raise ValueError(
                    (
                        f"No hay stock suficiente de "
                        f"'{product.name}'. "
                        f"Stock disponible: {product.stock}."
                    )
                )

        order = Order(
            user_id=user_id,
            status_id=pending_status.id,
            notes=notes,
        )

        db.session.add(order)

        for item in cart_items:
            product = item.product

            detail = OrderDetail(
                product_id=product.id,
                quantity=item.quantity,
                unit_price=product.retail_price,
                is_wholesale_price=False,
            )

            order.details.append(detail)

            product.stock -= item.quantity

        cart.items.clear()
        cart.updated_at = datetime.now(timezone.utc)

        OrderService._commit(
            "No fue posible crear el pedido."
        )

        return order

    @staticmethod
    def update_status(order, data):
        status_id = OrderService._validate_status_id(
            data.get("status_id")
        )

        new_status = db.session.get(
            OrderStatus,
            status_id,
        )

        if new_status is None:
            raise LookupError(
                "El estado seleccionado no existe."
            )

        current_name = order.status.name.upper()
        new_name = new_status.name.upper()

        if current_name == new_name:
            return order

        allowed_statuses = (
            OrderService.ALLOWED_TRANSITIONS.get(
                current_name,
                set(),
            )
        )

        if new_name not in allowed_statuses:
            raise ValueError(
                (
                    f"No se puede cambiar un pedido "
                    f"de {current_name} a {new_name}."
                )
            )

        if new_name == "CANCELADO":
            OrderService._restore_stock(order)

        order.status_id = new_status.id
        order.updated_at = datetime.now(timezone.utc)

        OrderService._commit(
            "No fue posible actualizar el estado del pedido."
        )

        return order

    @staticmethod
    def cancel_pending_order(order):
        current_status = order.status.name.upper()

        if current_status != "PENDIENTE":
            raise ValueError(
                (
                    "Solo se pueden cancelar pedidos "
                    "que se encuentren pendientes."
                )
            )

        cancelled_status = (
            OrderService._get_status_by_name(
                "CANCELADO"
            )
        )

        OrderService._restore_stock(order)

        order.status_id = cancelled_status.id
        order.updated_at = datetime.now(timezone.utc)

        OrderService._commit(
            "No fue posible cancelar el pedido."
        )

        return order

    @staticmethod
    def serialize(order):
        details_data = []
        total = Decimal("0.00")
        total_quantity = 0

        ordered_details = sorted(
            order.details,
            key=lambda detail: detail.id,
        )

        for detail in ordered_details:
            subtotal = (
                detail.unit_price * detail.quantity
            )

            total += subtotal
            total_quantity += detail.quantity

            details_data.append(
                {
                    "id": detail.id,
                    "product_id": detail.product_id,
                    "quantity": detail.quantity,
                    "unit_price": float(
                        detail.unit_price
                    ),
                    "subtotal": float(subtotal),
                    "is_wholesale_price": (
                        detail.is_wholesale_price
                    ),
                    "product": {
                        "id": detail.product.id,
                        "name": detail.product.name,
                        "image_url": (
                            detail.product.image_url
                        ),
                    },
                }
            )

        return {
            "id": order.id,
            "user_id": order.user_id,
            "status_id": order.status_id,
            "notes": order.notes,
            "ordered_at": order.ordered_at.isoformat(),
            "updated_at": order.updated_at.isoformat(),
            "total_quantity": total_quantity,
            "total": float(total),
            "status": {
                "id": order.status.id,
                "name": order.status.name,
                "description": order.status.description,
            },
            "user": {
                "id": order.user.id,
                "first_name": order.user.first_name,
                "last_name": order.user.last_name,
                "email": order.user.email,
            },
            "details": details_data,
        }

    @staticmethod
    def serialize_status(status):
        return {
            "id": status.id,
            "name": status.name,
            "description": status.description,
        }

    @staticmethod
    def _restore_stock(order):
        for detail in order.details:
            detail.product.stock += detail.quantity

    @staticmethod
    def _get_status_by_name(status_name):
        status = OrderStatus.query.filter(
            db.func.upper(OrderStatus.name)
            == status_name.upper()
        ).first()

        if status is None:
            raise RuntimeError(
                (
                    f"No se encuentra configurado el estado "
                    f"{status_name}."
                )
            )

        return status

    @staticmethod
    def _validate_status_id(status_id):
        if (
            isinstance(status_id, bool)
            or not isinstance(status_id, int)
            or status_id <= 0
        ):
            raise ValueError(
                "Debe seleccionar un estado válido."
            )

        return status_id

    @staticmethod
    def _validate_notes(notes):
        if notes is None:
            return None

        if not isinstance(notes, str):
            raise ValueError(
                "Las observaciones deben ser texto."
            )

        notes = notes.strip()

        return notes if notes else None

    @staticmethod
    def _commit(error_message):
        try:
            db.session.commit()
        except IntegrityError as error:
            db.session.rollback()

            raise ValueError(
                error_message
            ) from error