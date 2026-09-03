from decimal import Decimal, InvalidOperation

from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models.category import Category
from app.models.product import Product


class ProductService:
    @staticmethod
    def get_all():
        return Product.query.order_by(Product.name.asc()).all()

    @staticmethod
    def get_by_id(product_id):
        return db.session.get(Product, product_id)

    @staticmethod
    def create(data):
        category = ProductService._validate_category(
            data.get("category_id")
        )

        name = ProductService._validate_name(
            data.get("name")
        )

        description = ProductService._validate_description(
            data.get("description")
        )

        retail_price = ProductService._validate_price(
            data.get("retail_price"),
            "precio minorista",
        )

        wholesale_price = ProductService._validate_price(
            data.get("wholesale_price"),
            "precio mayorista",
        )

        minimum_quantity = (
            ProductService._validate_minimum_quantity(
                data.get("minimum_wholesale_quantity", 1)
            )
        )

        stock = ProductService._validate_stock(
            data.get("stock", 0)
        )

        image_url = ProductService._validate_image_url(
            data.get("image_url")
        )

        product = Product(
            category_id=category.id,
            name=name,
            description=description,
            retail_price=retail_price,
            wholesale_price=wholesale_price,
            minimum_wholesale_quantity=minimum_quantity,
            stock=stock,
            image_url=image_url,
        )

        db.session.add(product)
        ProductService._commit()

        return product

    @staticmethod
    def update(product, data):
        if not data:
            raise ValueError(
                "Debe enviar al menos un campo para actualizar."
            )

        allowed_fields = {
            "category_id",
            "name",
            "description",
            "retail_price",
            "wholesale_price",
            "minimum_wholesale_quantity",
            "stock",
            "image_url",
            "active",
        }

        if not any(field in data for field in allowed_fields):
            raise ValueError(
                "No se recibió ningún campo válido para actualizar."
            )

        if "category_id" in data:
            category = ProductService._validate_category(
                data.get("category_id")
            )
            product.category_id = category.id

        if "name" in data:
            product.name = ProductService._validate_name(
                data.get("name")
            )

        if "description" in data:
            product.description = (
                ProductService._validate_description(
                    data.get("description")
                )
            )

        if "retail_price" in data:
            product.retail_price = (
                ProductService._validate_price(
                    data.get("retail_price"),
                    "precio minorista",
                )
            )

        if "wholesale_price" in data:
            product.wholesale_price = (
                ProductService._validate_price(
                    data.get("wholesale_price"),
                    "precio mayorista",
                )
            )

        if "minimum_wholesale_quantity" in data:
            product.minimum_wholesale_quantity = (
                ProductService._validate_minimum_quantity(
                    data.get("minimum_wholesale_quantity")
                )
            )

        if "stock" in data:
            product.stock = ProductService._validate_stock(
                data.get("stock")
            )

        if "image_url" in data:
            product.image_url = (
                ProductService._validate_image_url(
                    data.get("image_url")
                )
            )

        if "active" in data:
            active = data.get("active")

            if not isinstance(active, bool):
                raise ValueError(
                    "El campo active debe ser verdadero o falso."
                )

            product.active = active

        ProductService._commit()

        return product

    @staticmethod
    def deactivate(product):
        product.active = False
        ProductService._commit()

        return product

    @staticmethod
    def _validate_category(category_id):
        if (
            isinstance(category_id, bool)
            or not isinstance(category_id, int)
            or category_id <= 0
        ):
            raise ValueError(
                "Debe seleccionar una categoría válida."
            )

        category = db.session.get(Category, category_id)

        if category is None:
            raise ValueError(
                "La categoría seleccionada no existe."
            )

        if not category.active:
            raise ValueError(
                "No se puede asignar una categoría inactiva."
            )

        return category

    @staticmethod
    def _validate_name(name):
        if not isinstance(name, str):
            raise ValueError(
                "El nombre del producto es obligatorio."
            )

        name = name.strip()

        if not name:
            raise ValueError(
                "El nombre del producto es obligatorio."
            )

        if len(name) > 150:
            raise ValueError(
                "El nombre no puede superar los 150 caracteres."
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

        return description or None

    @staticmethod
    def _validate_price(value, field_name):
        if value is None or isinstance(value, bool):
            raise ValueError(
                f"El {field_name} es obligatorio."
            )

        try:
            price = Decimal(str(value))
        except (InvalidOperation, TypeError, ValueError) as error:
            raise ValueError(
                f"El {field_name} debe ser un número válido."
            ) from error

        if not price.is_finite() or price < 0:
            raise ValueError(
                f"El {field_name} no puede ser negativo."
            )

        if price > Decimal("9999999999.99"):
            raise ValueError(
                f"El {field_name} supera el máximo permitido."
            )

        if price.as_tuple().exponent < -2:
            raise ValueError(
                f"El {field_name} puede tener como máximo dos decimales."
            )

        return price

    @staticmethod
    def _validate_minimum_quantity(quantity):
        if (
            isinstance(quantity, bool)
            or not isinstance(quantity, int)
            or quantity <= 0
        ):
            raise ValueError(
                "La cantidad mínima mayorista debe ser un entero mayor que cero."
            )

        return quantity

    @staticmethod
    def _validate_stock(stock):
        if (
            isinstance(stock, bool)
            or not isinstance(stock, int)
            or stock < 0
        ):
            raise ValueError(
                "El stock debe ser un entero mayor o igual que cero."
            )

        return stock

    @staticmethod
    def _validate_image_url(image_url):
        if image_url is None:
            return None

        if not isinstance(image_url, str):
            raise ValueError(
                "La URL de la imagen debe ser un texto."
            )

        image_url = image_url.strip()

        if len(image_url) > 500:
            raise ValueError(
                "La URL de la imagen no puede superar los 500 caracteres."
            )

        return image_url or None

    @staticmethod
    def _commit():
        try:
            db.session.commit()
        except IntegrityError as error:
            db.session.rollback()

            raise ValueError(
                "No fue posible guardar el producto. Verificá sus datos."
            ) from error