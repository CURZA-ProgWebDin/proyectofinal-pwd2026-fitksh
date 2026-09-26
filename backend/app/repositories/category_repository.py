from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models.category import Category


class CategoryRepository:
    @staticmethod
    def get_all():
        return Category.query.order_by(Category.name.asc()).all()

    @staticmethod
    def get_by_id(category_id):
        return db.session.get(Category, category_id)

    @staticmethod
    def name_exists(name, exclude_id=None):
        query = Category.query.filter(
            db.func.lower(Category.name) == name.lower()
        )

        if exclude_id is not None:
            query = query.filter(Category.id != exclude_id)

        return query.first() is not None

    @staticmethod
    def add(category):
        db.session.add(category)

    @staticmethod
    def commit():
        try:
            db.session.commit()
        except IntegrityError as error:
            db.session.rollback()

            raise FileExistsError(
                "No fue posible guardar la categoría "
                "porque sus datos están duplicados."
            ) from error