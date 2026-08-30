import re

from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models.role import Role
from app.models.user import User


class UserService:
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
    def get_active_roles():
        return Role.query.filter(
            Role.active.is_(True)
        ).order_by(
            Role.name.asc()
        ).all()

    @staticmethod
    def create(data):
        first_name = UserService._validate_name(
            data.get("first_name"),
            "nombre",
        )

        last_name = UserService._validate_name(
            data.get("last_name"),
            "apellido",
        )

        email = UserService._validate_email(
            data.get("email")
        )

        password = UserService._validate_password(
            data.get("password")
        )

        role = UserService._validate_role(
            data.get("role_id")
        )

        if UserService._email_exists(email):
            raise FileExistsError(
                "Ya existe un usuario registrado con ese email."
            )

        user = User(
            role_id=role.id,
            first_name=first_name,
            last_name=last_name,
            email=email,
        )

        user.set_password(password)

        db.session.add(user)
        UserService._commit()

        return user

    @staticmethod
    def update(user, data, current_user_id):
        if not data:
            raise ValueError(
                "Debe enviar al menos un campo para actualizar."
            )

        allowed_fields = {
            "first_name",
            "last_name",
            "email",
            "password",
            "role_id",
            "active",
        }

        if not any(field in data for field in allowed_fields):
            raise ValueError(
                "No se recibió ningún campo válido para actualizar."
            )

        new_first_name = user.first_name
        new_last_name = user.last_name
        new_email = user.email
        new_role = user.role
        new_active = user.active
        new_password = None

        if "first_name" in data:
            new_first_name = UserService._validate_name(
                data.get("first_name"),
                "nombre",
            )

        if "last_name" in data:
            new_last_name = UserService._validate_name(
                data.get("last_name"),
                "apellido",
            )

        if "email" in data:
            new_email = UserService._validate_email(
                data.get("email")
            )

            if UserService._email_exists(
                new_email,
                exclude_id=user.id,
            ):
                raise FileExistsError(
                    "Ya existe un usuario registrado con ese email."
                )

        if "password" in data:
            new_password = UserService._validate_password(
                data.get("password")
            )

        if "role_id" in data:
            new_role = UserService._validate_role(
                data.get("role_id")
            )

        if "active" in data:
            new_active = data.get("active")

            if not isinstance(new_active, bool):
                raise ValueError(
                    "El campo active debe ser verdadero o falso."
                )

        new_role_name = new_role.name.upper()

        if user.id == current_user_id:
            if not new_active:
                raise PermissionError(
                    "No puede desactivar su propio usuario."
                )

            if new_role_name != "ADMINISTRADOR":
                raise PermissionError(
                    "No puede quitarse su propio rol de administrador."
                )

        currently_active_admin = (
            user.active
            and user.role is not None
            and user.role.name.upper() == "ADMINISTRADOR"
        )

        removes_admin_access = (
            not new_active
            or new_role_name != "ADMINISTRADOR"
        )

        if (
            currently_active_admin
            and removes_admin_access
            and UserService._active_admin_count() <= 1
        ):
            raise PermissionError(
                "Debe existir al menos un administrador activo."
            )

        user.first_name = new_first_name
        user.last_name = new_last_name
        user.email = new_email
        user.role_id = new_role.id
        user.active = new_active

        if new_password is not None:
            user.set_password(new_password)

        UserService._commit()

        return user

    @staticmethod
    def deactivate(user, current_user_id):
        if user.id == current_user_id:
            raise PermissionError(
                "No puede desactivar su propio usuario."
            )

        is_active_admin = (
            user.active
            and user.role is not None
            and user.role.name.upper() == "ADMINISTRADOR"
        )

        if (
            is_active_admin
            and UserService._active_admin_count() <= 1
        ):
            raise PermissionError(
                "Debe existir al menos un administrador activo."
            )

        user.active = False
        UserService._commit()

        return user

    @staticmethod
    def _validate_role(role_id):
        if (
            isinstance(role_id, bool)
            or not isinstance(role_id, int)
            or role_id <= 0
        ):
            raise ValueError(
                "Debe seleccionar un rol válido."
            )

        role = db.session.get(Role, role_id)

        if role is None:
            raise ValueError(
                "El rol seleccionado no existe."
            )

        if not role.active:
            raise ValueError(
                "El rol seleccionado se encuentra inactivo."
            )

        return role

    @staticmethod
    def _validate_name(value, field_name):
        if not isinstance(value, str):
            raise ValueError(
                f"El {field_name} es obligatorio."
            )

        value = value.strip()

        if not value:
            raise ValueError(
                f"El {field_name} es obligatorio."
            )

        if len(value) > 80:
            raise ValueError(
                f"El {field_name} no puede superar los 80 caracteres."
            )

        return value

    @staticmethod
    def _validate_email(email):
        if not isinstance(email, str):
            raise ValueError(
                "El email es obligatorio."
            )

        email = email.strip().lower()

        if not email:
            raise ValueError(
                "El email es obligatorio."
            )

        if len(email) > 150:
            raise ValueError(
                "El email no puede superar los 150 caracteres."
            )

        email_pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

        if re.fullmatch(email_pattern, email) is None:
            raise ValueError(
                "El formato del email no es válido."
            )

        return email

    @staticmethod
    def _validate_password(password):
        if not isinstance(password, str):
            raise ValueError(
                "La contraseña es obligatoria."
            )

        if len(password) < 8:
            raise ValueError(
                "La contraseña debe tener al menos 8 caracteres."
            )

        if len(password) > 128:
            raise ValueError(
                "La contraseña no puede superar los 128 caracteres."
            )

        if not any(character.isalpha() for character in password):
            raise ValueError(
                "La contraseña debe contener al menos una letra."
            )

        if not any(character.isdigit() for character in password):
            raise ValueError(
                "La contraseña debe contener al menos un número."
            )

        return password

    @staticmethod
    def _email_exists(email, exclude_id=None):
        query = User.query.filter(
            db.func.lower(User.email) == email
        )

        if exclude_id is not None:
            query = query.filter(
                User.id != exclude_id
            )

        return query.first() is not None

    @staticmethod
    def _active_admin_count():
        return User.query.join(Role).filter(
            User.active.is_(True),
            db.func.upper(Role.name) == "ADMINISTRADOR",
        ).count()

    @staticmethod
    def _commit():
        try:
            db.session.commit()
        except IntegrityError as error:
            db.session.rollback()

            raise FileExistsError(
                "No fue posible guardar el usuario."
            ) from error