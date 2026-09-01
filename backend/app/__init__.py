from flask import Flask

from app.commands import create_admin_command

from app.config import Config
from app.extensions import cors, db, jwt, migrate
from app.models import (
    Cart,
    CartItem,
    Category,
    Order,
    OrderDetail,
    OrderStatus,
    Product,
    Role,
    User,
)

from app.routes.auth_routes import auth_bp
from app.routes.category_routes import category_bp
from app.routes.health import health_bp
from app.routes.product_routes import product_bp
from app.routes.user_routes import role_bp, user_bp
from app.routes.cart_routes import cart_bp


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    if not app.config.get("JWT_SECRET_KEY"):
        raise RuntimeError(
            "La variable JWT_SECRET_KEY no está configurada."
        )

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    cors.init_app(
        app,
        resources={
            r"/api/*": {
                "origins": "http://localhost:5173",
            }
        },
    )

    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(category_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(role_bp)
    app.register_blueprint(cart_bp)

    app.cli.add_command(create_admin_command)
    return app