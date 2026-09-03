import re

from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    decode_token,
)
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models.role import Role
from app.models.user import User
from app.models.refresh_token import RefreshToken

from datetime import datetime, timezone

class AuthService:
   
    @staticmethod
    def register(data):
        return AuthService._create_user(
            data,
            role_name="CLIENTE",
        )

    @staticmethod
    def create_admin(data):
        return AuthService._create_user(
            data,
            role_name="ADMINISTRADOR",
        )

    @staticmethod
    def _create_user(data, role_name):
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

        role_name = role_name.upper()

        role = Role.query.filter(
            db.func.upper(Role.name) == role_name,
            Role.active.is_(True),
        ).first()

        if role is None:
            raise RuntimeError(
                f"No se encuentra configurado el rol {role_name}."
            )

        user = User(
            role_id=role.id,
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
    def login(data):
        email = AuthService._validate_email(
            data.get("email")
        )

        password = data.get("password")

        if not isinstance(password, str) or not password:
            raise ValueError(
                "La contraseña es obligatoria."
            )

        user = User.query.filter(
            db.func.lower(User.email) == email
        ).first()

        if user is None or not user.check_password(password):
            raise PermissionError(
                "Email o contraseña incorrectos."
            )

        if not user.active:
            raise PermissionError(
                "El usuario se encuentra desactivado."
            )

        if user.role is None or not user.role.active:
            raise PermissionError(
                "El rol del usuario no se encuentra disponible."
            )

        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={
                "role": user.role.name,
            },
        )
        
        refresh_token = create_refresh_token(
            identity=str(user.id),
        )

        refresh_token_data = decode_token(refresh_token)

        stored_refresh_token = RefreshToken(
            user_id=user.id,
            token_identifier=refresh_token_data["jti"],
            expires_at=datetime.fromtimestamp(
                refresh_token_data["exp"],
                tz=timezone.utc,
            ),
        )

        db.session.add(stored_refresh_token)
        db.session.commit()

        return user, access_token, refresh_token
    
    @staticmethod
    def refresh_access_token(identity, token_identifier):
        user = AuthService.get_authenticated_user(identity)

        stored_refresh_token = RefreshToken.query.filter(
            RefreshToken.user_id == user.id,
            RefreshToken.token_identifier == token_identifier,
        ).first()

        if stored_refresh_token is None:
            raise PermissionError(
                "El refresh token no se encuentra registrado."
            )

        if stored_refresh_token.revoked_at is not None:
            raise PermissionError(
                "El refresh token fue revocado."
            )

        if stored_refresh_token.expires_at <= datetime.now(timezone.utc):
            raise PermissionError(
                "El refresh token se encuentra vencido."
            )

        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={
                "role": user.role.name,
            },
        )

        return access_token

    @staticmethod
    def revoke_refresh_token(identity, token_identifier):
        try:
            user_id = int(identity)
        except (TypeError, ValueError) as error:
            raise PermissionError(
                "La identidad del token no es válida."
            ) from error

        stored_refresh_token = RefreshToken.query.filter(
            RefreshToken.user_id == user_id,
            RefreshToken.token_identifier == token_identifier,
        ).first()

        if stored_refresh_token is None:
            raise PermissionError(
                "El refresh token no se encuentra registrado."
            )

        if stored_refresh_token.revoked_at is None:
            stored_refresh_token.revoked_at = datetime.now(
                timezone.utc
            )

            db.session.commit()
            
    @staticmethod
    def get_authenticated_user(identity):
        
        try:
            user_id = int(identity)
        except (TypeError, ValueError) as error:
            raise PermissionError(
                "La identidad del token no es válida."
            ) from error

        user = db.session.get(User, user_id)

        if user is None or not user.active:
            raise PermissionError(
                "El usuario asociado al token no está disponible."
            )

        if user.role is None or not user.role.active:
            raise PermissionError(
                "El rol del usuario no está disponible."
            )

        return user
    
    # ------------------------------------------------------
    ## Validation methods
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