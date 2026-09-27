from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models.cart import Cart
from app.models.cart_item import CartItem


class CartRepository:
    @staticmethod
    def get_by_user_id(user_id):
        return Cart.query.filter_by(
            user_id=user_id
        ).first()

    @staticmethod
    def get_item_for_user(user_id, item_id):
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
    def add(cart):
        db.session.add(cart)

    @staticmethod
    def delete_item(item):
        db.session.delete(item)

    @staticmethod
    def commit():
        try:
            db.session.commit()
        except IntegrityError as error:
            db.session.rollback()

            raise ValueError(
                "No fue posible actualizar el carrito."
            ) from error