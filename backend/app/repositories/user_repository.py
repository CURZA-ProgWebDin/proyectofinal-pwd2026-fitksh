from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models.role import Role
from app.models.user import User


class UserRepository:
    @staticmethod
    def get_all():
        return User.query.order_by(
            User.last_name.asc(),
            User.first_name.asc(),
        ).all()

    @staticmethod
    def get_by_id(user_id):
        return db.session.get(User, user_id)

    @staticmethod
    def email_exists(email, exclude_id=None):
        query = User.query.filter(
            db.func.lower(User.email) == email
        )

        if exclude_id is not None:
            query = query.filter(User.id != exclude_id)

        return query.first() is not None

    @staticmethod
    def count_active_admins():
        return User.query.join(Role).filter(
            User.active.is_(True),
            db.func.upper(Role.name) == "ADMINISTRADOR",
        ).count()

    @staticmethod
    def add(user):
        db.session.add(user)

    @staticmethod
    def commit():
        try:
            db.session.commit()
        except IntegrityError as error:
            db.session.rollback()

            raise FileExistsError(
                "No fue posible guardar el usuario."
            ) from error