from datetime import datetime, timezone

from app.extensions import db


class CartItem(db.Model):
    __tablename__ = "carrito_items"

    id = db.Column(
        "id_carrito_item",
        db.BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    cart_id = db.Column(
        "id_carrito",
        db.BigInteger,
        db.ForeignKey(
            "carritos.id_carrito",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    product_id = db.Column(
        "id_producto",
        db.BigInteger,
        db.ForeignKey(
            "productos.id_producto",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    quantity = db.Column(
        "cantidad",
        db.Integer,
        nullable=False,
    )

    added_at = db.Column(
        "agregado_en",
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default=db.func.now(),
    )

    cart = db.relationship(
        "Cart",
        back_populates="items",
    )

    product = db.relationship(
        "Product",
        back_populates="cart_items",
    )

    __table_args__ = (
        db.UniqueConstraint(
            "id_carrito",
            "id_producto",
            name="uq_carrito_producto",
        ),
        db.CheckConstraint(
            "cantidad > 0",
            name="chk_carrito_cantidad",
        ),
    )