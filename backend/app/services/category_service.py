from app.models.category import Category
from app.repositories.category_repository import CategoryRepository


class CategoryService:
    @staticmethod
    def get_all():
        return CategoryRepository.get_all()

    @staticmethod
    def get_by_id(category_id):
        return CategoryRepository.get_by_id(category_id)

    @staticmethod
    def create(data):
        name = CategoryService._validate_name(data.get("name"))
        description = CategoryService._validate_description(
            data.get("description")
        )

        if CategoryRepository.name_exists(name):
            raise FileExistsError(
                "Ya existe una categoría con ese nombre."
            )

        category = Category(
            name=name,
            description=description,
        )

        CategoryRepository.add(category)
        CategoryRepository.commit()

        return category

    @staticmethod
    def update(category, data):
        if not data:
            raise ValueError(
                "Debe enviar al menos un campo para actualizar."
            )

        if "name" in data:
            name = CategoryService._validate_name(data.get("name"))

            if CategoryRepository.name_exists(
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

        CategoryRepository.commit()

        return category

    @staticmethod
    def deactivate(category):
        category.active = False
        CategoryRepository.commit()

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