from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models.product import Product


class ProductRepository:
    @staticmethod
    def get_all():
        return Product.query.order_by(Product.name.asc()).all()

    @staticmethod
    def get_by_id(product_id):
        return db.session.get(Product, product_id)

    @staticmethod
    def add(product):
        db.session.add(product)

    @staticmethod
    def commit():
        try:
            db.session.commit()
        except IntegrityError as error:
            db.session.rollback()

            raise ValueError(
                "No fue posible guardar el producto. Verificá sus datos."
            ) from error