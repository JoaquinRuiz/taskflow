from flask import Flask

from app.config import Config
from app.extensions import db, ma
from app.views import blueprints


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    ma.init_app(app)

    for bp in blueprints:
        app.register_blueprint(bp)

    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    with app.app_context():
        from app.models import User, Project, Task, Tag  # noqa: F401
        db.create_all()

    return app
