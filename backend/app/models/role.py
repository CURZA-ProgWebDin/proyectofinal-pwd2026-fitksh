from datetime import datetime, timezone

from app.extensions import db


class Role(db.Model):
    __tablename__ = "roles"

    id = db.Column(
        "id_rol",
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

    users = db.relationship(
        "User",
        back_populates="role",
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "active": self.active,
            "created_at": self.created_at.isoformat(),
        }