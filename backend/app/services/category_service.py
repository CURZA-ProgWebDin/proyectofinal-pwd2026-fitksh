from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models.category import Category


class CategoryService:
    @staticmethod
    def get_all():
        return Category.query.order_by(Category.name.asc()).all()

    @staticmethod
    def get_by_id(category_id):
        return db.session.get(Category, category_id)

    @staticmethod
    def create(data):
        name = CategoryService._validate_name(data.get("name"))
        description = CategoryService._validate_description(
            data.get("description")
        )

        if CategoryService._name_exists(name):
            raise FileExistsError(
                "Ya existe una categoría con ese nombre."
            )

        category = Category(
            name=name,
            description=description,
        )

        db.session.add(category)
        CategoryService._commit()

        return category

    @staticmethod
    def update(category, data):
        if not data:
            raise ValueError(
                "Debe enviar al menos un campo para actualizar."
            )

        if "name" in data:
            name = CategoryService._validate_name(data.get("name"))

            if CategoryService._name_exists(
                name,
                exclude_id=category.id,
            ):
                raise FileExistsError(
                    "Ya existe una categoría con ese nombre."
                )

            category.name = name

        if "description" in data:
            category.description = (
                CategoryService._validate_description(
                    data.get("description")
                )
            )

        if "active" in data:
            active = data.get("active")

            if not isinstance(active, bool):
                raise ValueError(
                    "El campo active debe ser verdadero o falso."
                )

            category.active = active

        CategoryService._commit()

        return category

    @staticmethod
    def deactivate(category):
        category.active = False
        CategoryService._commit()

        return category

    @staticmethod
    def _validate_name(name):
        if not isinstance(name, str):
            raise ValueError(
                "El nombre de la categoría es obligatorio."
            )

        name = name.strip()

        if not name:
            raise ValueError(
                "El nombre de la categoría es obligatorio."
            )

        if len(name) > 100:
            raise ValueError(
                "El nombre no puede superar los 100 caracteres."
            )

        return name

    @staticmethod
    def _validate_description(description):
        if description is None:
            return None

        if not isinstance(description, str):
            raise ValueError(
                "La descripción debe ser un texto."
            )

        description = description.strip()

        if len(description) > 255:
            raise ValueError(
                "La descripción no puede superar los 255 caracteres."
            )

        return description or None

    @staticmethod
    def _name_exists(name, exclude_id=None):
        query = Category.query.filter(
            db.func.lower(Category.name) == name.lower()
        )

        if exclude_id is not None:
            query = query.filter(Category.id != exclude_id)

        return query.first() is not None

    @staticmethod
    def _commit():
        try:
            db.session.commit()
        except IntegrityError as error:
            db.session.rollback()

            raise FileExistsError(
                "No fue posible guardar la categoría porque sus datos están duplicados."
            ) from error