from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models.refresh_token import RefreshToken


class RefreshTokenRepository:
    @staticmethod
    def get_by_identifier(user_id, token_identifier):
        return RefreshToken.query.filter(
            RefreshToken.user_id == user_id,
            RefreshToken.token_identifier == token_identifier,
        ).first()

    @staticmethod
    def add(refresh_token):
        db.session.add(refresh_token)

    @staticmethod
    def commit():
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            raise