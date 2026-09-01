from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.product import Product


class CartService:
    @staticmethod
    def get_by_user_id(user_id):
        return Cart.query.filter_by(
            user_id=user_id
        ).first()

    @staticmethod
    def add_item(user_id, data):
        product_id = CartService._validate_product_id(
            data.get("product_id")
        )

        quantity = CartService._validate_quantity(
            data.get("quantity")
        )

        product = CartService._get_available_product(
            product_id
        )

        cart = CartService._get_or_create_cart(user_id)

        item = next(
            (
                current_item
                for current_item in cart.items
                if current_item.product_id == product.id
            ),
            None,
        )

        if item is None:
            new_quantity = quantity
            created = True
        else:
            new_quantity = item.quantity + quantity
            created = False

        CartService._validate_stock(
            product,
            new_quantity,
        )

        if item is None:
            item = CartItem(
                product_id=product.id,
                quantity=new_quantity,
            )
            cart.items.append(item)
        else:
            item.quantity = new_quantity

        CartService._touch(cart)
        CartService._commit()

        return cart, created

    @staticmethod
    def update_item(user_id, item_id, data):
        item = CartService._get_item_for_user(
            user_id,
            item_id,
        )

        if item is None:
            raise LookupError(
                "El producto no se encuentra en tu carrito."
            )

        quantity = CartService._validate_quantity(
            data.get("quantity")
        )

        product = CartService._get_available_product(
            item.product_id
        )

        CartService._validate_stock(
            product,
            quantity,
        )

        item.quantity = quantity

        CartService._touch(item.cart)
        CartService._commit()

        return item.cart

    @staticmethod
    def remove_item(user_id, item_id):
        item = CartService._get_item_for_user(
            user_id,
            item_id,
        )

        if item is None:
            raise LookupError(
                "El producto no se encuentra en tu carrito."
            )

        cart = item.cart

        db.session.delete(item)

        CartService._touch(cart)
        CartService._commit()

        return cart

    @staticmethod
    def clear(user_id):
        cart = CartService.get_by_user_id(user_id)

        if cart is None:
            return None

        cart.items.clear()

        CartService._touch(cart)
        CartService._commit()

        return cart

    @staticmethod
    def serialize(cart):
        if cart is None:
            return {
                "id": None,
                "user_id": None,
                "items": [],
                "item_count": 0,
                "total_quantity": 0,
                "total": 0.0,
                "created_at": None,
                "updated_at": None,
            }

        items_data = []
        total = Decimal("0.00")
        total_quantity = 0

        ordered_items = sorted(
            cart.items,
            key=lambda item: item.added_at,
        )

        for item in ordered_items:
            product = item.product
            unit_price = product.retail_price
            subtotal = unit_price * item.quantity

            total += subtotal
            total_quantity += item.quantity

            items_data.append(
                {
                    "id": item.id,
                    "product_id": item.product_id,
                    "quantity": item.quantity,
                    "unit_price": float(unit_price),
                    "subtotal": float(subtotal),
                    "added_at": item.added_at.isoformat(),
                    "product": {
                        "id": product.id,
                        "name": product.name,
                        "image_url": product.image_url,
                        "stock": product.stock,
                        "active": product.active,
                    },
                }
            )

        return {
            "id": cart.id,
            "user_id": cart.user_id,
            "items": items_data,
            "item_count": len(items_data),
            "total_quantity": total_quantity,
            "total": float(total),
            "created_at": cart.created_at.isoformat(),
            "updated_at": cart.updated_at.isoformat(),
        }

    @staticmethod
    def _get_or_create_cart(user_id):
        cart = CartService.get_by_user_id(user_id)

        if cart is None:
            cart = Cart(user_id=user_id)
            db.session.add(cart)

        return cart

    @staticmethod
    def _get_item_for_user(user_id, item_id):
        return (
            CartItem.query
            .join(Cart)
            .filter(
                CartItem.id == item_id,
                Cart.user_id == user_id,
            )
            .first()
        )

    @staticmethod
    def _get_available_product(product_id):
        product = db.session.get(Product, product_id)

        if product is None:
            raise LookupError(
                "El producto seleccionado no existe."
            )

        if not product.active:
            raise ValueError(
                "El producto seleccionado no está disponible."
            )

        return product

    @staticmethod
    def _validate_product_id(product_id):
        if (
            isinstance(product_id, bool)
            or not isinstance(product_id, int)
            or product_id <= 0
        ):
            raise ValueError(
                "Debe seleccionar un producto válido."
            )

        return product_id

    @staticmethod
    def _validate_quantity(quantity):
        if (
            isinstance(quantity, bool)
            or not isinstance(quantity, int)
            or quantity <= 0
        ):
            raise ValueError(
                "La cantidad debe ser un entero mayor que cero."
            )

        return quantity

    @staticmethod
    def _validate_stock(product, quantity):
        if quantity > product.stock:
            raise ValueError(
                (
                    f"Solo hay {product.stock} unidades "
                    "disponibles del producto."
                )
            )

    @staticmethod
    def _touch(cart):
        cart.updated_at = datetime.now(timezone.utc)

    @staticmethod
    def _commit():
        try:
            db.session.commit()
        except IntegrityError as error:
            db.session.rollback()

            raise ValueError(
                "No fue posible actualizar el carrito."
            ) from error