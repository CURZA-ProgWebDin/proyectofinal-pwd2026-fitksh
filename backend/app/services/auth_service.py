import re

from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models.role import Role
from app.models.user import User


class AuthService:
    @staticmethod
    def register(data):
        first_name = AuthService._validate_name(
            data.get("first_name"),
            "nombre",
        )

        last_name = AuthService._validate_name(
            data.get("last_name"),
            "apellido",
        )

        email = AuthService._validate_email(
            data.get("email")
        )

        password = AuthService._validate_password(
            data.get("password")
        )

        if AuthService._email_exists(email):
            raise FileExistsError(
                "Ya existe un usuario registrado con ese email."
            )

        customer_role = Role.query.filter(
            db.func.upper(Role.name) == "CLIENTE",
            Role.active.is_(True),
        ).first()

        if customer_role is None:
            raise RuntimeError(
                "No se encuentra configurado el rol CLIENTE."
            )

        user = User(
            role_id=customer_role.id,
            first_name=first_name,
            last_name=last_name,
            email=email,
        )

        user.set_password(password)

        db.session.add(user)

        try:
            db.session.commit()
        except IntegrityError as error:
            db.session.rollback()

            raise FileExistsError(
                "Ya existe un usuario registrado con ese email."
            ) from error

        return user

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
    def _email_exists(email):
        return User.query.filter(
            db.func.lower(User.email) == email
        ).first() is not None