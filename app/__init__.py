from flask import Flask

from app.config import Config
from app.extensions import db, migrate
from app.routes import register_blueprints
from app.utils.errors import register_error_handlers


def create_app(config=None):
    app = Flask(__name__)
    app.config.from_object(Config)

    if config:
        app.config.from_mapping(config)

    db.init_app(app)
    migrate.init_app(app, db)

    # Imported so Alembic sees every table when generating migrations.
    from app import models  # noqa: F401
    from app.seed import seed_command

    register_blueprints(app)
    register_error_handlers(app)
    app.cli.add_command(seed_command)

    return app
