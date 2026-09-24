from app.extensions import db
from app.models.role import Role


class RoleRepository:
    @staticmethod
    def get_by_id(role_id):
        return db.session.get(Role, role_id)

    @staticmethod
    def get_active():
        return Role.query.filter(
            Role.active.is_(True)
        ).order_by(
            Role.name.asc()
        ).all()

    @staticmethod
    def get_active_by_name(name):
        return Role.query.filter(
            db.func.upper(Role.name) == name.upper(),
            Role.active.is_(True),
        ).first()