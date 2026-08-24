from flask import Flask

from app.config import Config
from app.extensions import cors, db, migrate
from app.routes.health import health_bp


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(
        app,
        resources={
            r"/api/*": {
                "origins": "http://localhost:5173",
            }
        },
    )

    app.register_blueprint(health_bp)

    return app