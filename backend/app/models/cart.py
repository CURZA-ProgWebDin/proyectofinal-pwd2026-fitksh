from datetime import datetime, timezone

from app.extensions import db


class Cart(db.Model):
    __tablename__ = "carritos"

    id = db.Column(
        "id_carrito",
        db.BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    user_id = db.Column(
        "id_usuario",
        db.BigInteger,
        db.ForeignKey(
            "usuarios.id_usuario",
            ondelete="CASCADE",
        ),
        nullable=False,
        unique=True,
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

    user = db.relationship(
        "User",
        back_populates="cart",
    )

    items = db.relationship(
        "CartItem",
        back_populates="cart",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )