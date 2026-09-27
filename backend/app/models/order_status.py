from app.extensions import db


class OrderStatus(db.Model):
    __tablename__ = "estados_pedido"

    id = db.Column(
        "id_estado_pedido",
        db.Integer,
        primary_key=True,
        autoincrement=True,
    )

    name = db.Column(
        "nombre",
        db.String(30),
        nullable=False,
        unique=True,
    )

    description = db.Column(
        "descripcion",
        db.String(255),
        nullable=True,
    )

    orders = db.relationship(
        "Order",
        back_populates="status",
        passive_deletes=True,
    )