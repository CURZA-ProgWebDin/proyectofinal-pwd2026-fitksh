from datetime import datetime, timezone

from werkzeug.security import (
    check_password_hash,
    generate_password_hash,
)

from app.extensions import db


class User(db.Model):
    __tablename__ = "usuarios"

    id = db.Column(
        "id_usuario",
        db.BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    role_id = db.Column(
        "id_rol",
        db.Integer,
        db.ForeignKey(
            "roles.id_rol",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    first_name = db.Column(
        "nombre",
        db.String(80),
        nullable=False,
    )

    last_name = db.Column(
        "apellido",
        db.String(80),
        nullable=False,
    )

    email = db.Column(
        "email",
        db.String(150),
        nullable=False,
        unique=True,
    )

    password_hash = db.Column(
        "password_hash",
        db.String(255),
        nullable=False,
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

    role = db.relationship(
        "Role",
        back_populates="users",
    )
    
    cart = db.relationship(
        "Cart",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    
    orders = db.relationship(
        "Order",
        back_populates="user",
        passive_deletes=True,
    )
    
    refresh_tokens = db.relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(
            self.password_hash,
            password,
        )

    def to_dict(self):
        return {
            "id": self.id,
            "role_id": self.role_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "active": self.active,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "role": {
                "id": self.role.id,
                "name": self.role.name,
            } if self.role else None,
        }