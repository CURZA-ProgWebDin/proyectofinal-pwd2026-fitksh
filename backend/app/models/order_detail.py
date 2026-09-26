from app.extensions import db


class OrderDetail(db.Model):
    __tablename__ = "pedido_detalles"

    id = db.Column(
        "id_pedido_detalle",
        db.BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    order_id = db.Column(
        "id_pedido",
        db.BigInteger,
        db.ForeignKey(
            "pedidos.id_pedido",
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

    unit_price = db.Column(
        "precio_unitario",
        db.Numeric(12, 2),
        nullable=False,
    )

    is_wholesale_price = db.Column(
        "es_precio_mayorista",
        db.Boolean,
        nullable=False,
        default=False,
        server_default=db.false(),
    )

    order = db.relationship(
        "Order",
        back_populates="details",
    )

    product = db.relationship(
        "Product",
        back_populates="order_details",
    )

    __table_args__ = (
        db.UniqueConstraint(
            "id_pedido",
            "id_producto",
            name="uq_pedido_producto",
        ),
        db.CheckConstraint(
            "cantidad > 0",
            name="chk_detalle_cantidad",
        ),
        db.CheckConstraint(
            "precio_unitario >= 0",
            name="chk_detalle_precio",
        ),
    )