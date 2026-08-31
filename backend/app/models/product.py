from datetime import datetime, timezone

from app.extensions import db


class Product(db.Model):
    __tablename__ = "productos"

    id = db.Column(
        "id_producto",
        db.BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    category_id = db.Column(
        "id_categoria",
        db.BigInteger,
        db.ForeignKey(
            "categorias.id_categoria",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    name = db.Column(
        "nombre",
        db.String(150),
        nullable=False,
    )

    description = db.Column(
        "descripcion",
        db.Text,
        nullable=True,
    )

    retail_price = db.Column(
        "precio_minorista",
        db.Numeric(12, 2),
        nullable=False,
    )

    wholesale_price = db.Column(
        "precio_mayorista",
        db.Numeric(12, 2),
        nullable=False,
    )

    minimum_wholesale_quantity = db.Column(
        "cantidad_minima_mayorista",
        db.Integer,
        nullable=False,
        default=1,
        server_default=db.text("1"),
    )

    stock = db.Column(
        "stock",
        db.Integer,
        nullable=False,
        default=0,
        server_default=db.text("0"),
    )

    image_url = db.Column(
        "imagen_url",
        db.String(500),
        nullable=True,
    )

    active = db.Column(
        "activo",
        db.Boolean,
        nullable=False,
        default=True,
        server_default=db.true(),
    )

    created_at = db.Column(
        "creado_en",
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default=db.func.now(),
    )

    updated_at = db.Column(
        "actualizado_en",
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        server_default=db.func.now(),
    )

    category = db.relationship(
        "Category",
        back_populates="products",
    )
    
    
    cart_items = db.relationship(
        "CartItem",
        back_populates="product",
        passive_deletes=True,
    )

    __table_args__ = (
        db.CheckConstraint(
            "precio_minorista >= 0",
            name="chk_precio_minorista",
        ),
        db.CheckConstraint(
            "precio_mayorista >= 0",
            name="chk_precio_mayorista",
        ),
        db.CheckConstraint(
            "cantidad_minima_mayorista > 0",
            name="chk_cantidad_mayorista",
        ),
        db.CheckConstraint(
            "stock >= 0",
            name="chk_stock",
        ),
        db.Index(
            "idx_productos_nombre",
            "nombre",
        ),
        db.Index(
            "idx_productos_categoria",
            "id_categoria",
        ),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "category_id": self.category_id,
            "name": self.name,
            "description": self.description,
            "retail_price": float(self.retail_price),
            "wholesale_price": float(self.wholesale_price),
            "minimum_wholesale_quantity": (
                self.minimum_wholesale_quantity
            ),
            "stock": self.stock,
            "image_url": self.image_url,
            "active": self.active,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "category": {
                "id": self.category.id,
                "name": self.category.name,
            } if self.category else None,
        }