from datetime import datetime, timezone

from app.extensions import db


class RefreshToken(db.Model):
    __tablename__ = "refresh_tokens"

    id = db.Column(
        "id_refresh_token",
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
    )

    token_identifier = db.Column(
        "identificador_token",
        db.String(255),
        nullable=False,
        unique=True,
    )

    expires_at = db.Column(
        "expira_en",
        db.DateTime(timezone=True),
        nullable=False,
    )

    revoked_at = db.Column(
        "revocado_en",
        db.DateTime(timezone=True),
        nullable=True,
    )

    created_at = db.Column(
        "creado_en",
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default=db.func.now(),
    )

    user = db.relationship(
        "User",
        back_populates="refresh_tokens",
    )