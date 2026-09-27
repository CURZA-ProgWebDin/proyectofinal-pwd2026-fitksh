from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models.order import Order
from app.models.order_status import OrderStatus


class OrderRepository:
    @staticmethod
    def get_all(user_id=None):
        query = Order.query

        if user_id is not None:
            query = query.filter_by(user_id=user_id)

        return query.order_by(
            Order.ordered_at.desc()
        ).all()

    @staticmethod
    def get_by_id(order_id):
        return db.session.get(Order, order_id)

    @staticmethod
    def get_statuses():
        return OrderStatus.query.order_by(
            OrderStatus.id
        ).all()

    @staticmethod
    def get_status_by_id(status_id):
        return db.session.get(OrderStatus, status_id)

    @staticmethod
    def get_status_by_name(name):
        return OrderStatus.query.filter(
            db.func.upper(OrderStatus.name) == name.upper()
        ).first()

    @staticmethod
    def add(order):
        db.session.add(order)

    @staticmethod
    def commit(error_message):
        try:
            db.session.commit()
        except IntegrityError as error:
            db.session.rollback()

            raise ValueError(error_message) from error