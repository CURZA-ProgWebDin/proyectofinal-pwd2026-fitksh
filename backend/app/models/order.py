from datetime import datetime, timezone

from app.extensions import db


class Order(db.Model):
    __tablename__ = "pedidos"

    id = db.Column(
        "id_pedido",
        db.BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    user_id = db.Column(
        "id_usuario",
        db.BigInteger,
        db.ForeignKey(
            "usuarios.id_usuario",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    status_id = db.Column(
        "id_estado_pedido",
        db.Integer,
        db.ForeignKey(
            "estados_pedido.id_estado_pedido",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    ordered_at = db.Column(
        "fecha_pedido",
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default=db.func.now(),
    )

    notes = db.Column(
        "observaciones",
        db.Text,
        nullable=True,
    )

    updated_at = db.Column(
        "actualizado_en",
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        server_default=db.func.now(),
    )

    user = db.relationship(
        "User",
        back_populates="orders",
    )

    status = db.relationship(
        "OrderStatus",
        back_populates="orders",
    )

    details = db.relationship(
        "OrderDetail",
        back_populates="order",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    __table_args__ = (
        db.Index(
            "idx_pedidos_usuario",
            "id_usuario",
        ),
        db.Index(
            "idx_pedidos_estado",
            "id_estado_pedido",
        ),
    )