import os
from pathlib import Path

from flask import Flask


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("TRACKER_SECRET_KEY"),
        DATABASE=str(Path(app.instance_path) / "nutrition.sqlite3"),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        MAX_CONTENT_LENGTH=64 * 1024,
    )
    if test_config:
        app.config.update(test_config)
    if not app.config["SECRET_KEY"]:
        raise RuntimeError("Set TRACKER_SECRET_KEY before starting the application.")
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    from . import db

    app.teardown_appcontext(db.close_db)
    app.cli.add_command(db.init_db_command)
    from . import routes

    routes.register(app)
    return app