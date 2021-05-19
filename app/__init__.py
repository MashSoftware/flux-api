import logging

from config import Config
from flask import Flask
from flask_compress import Compress
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

compress = Compress()
db = SQLAlchemy()
limiter = Limiter(key_func=get_remote_address, default_limits=["2 per second", "60 per minute"])
migrate = Migrate()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    compress.init_app(app)
    db.init_app(app)
    limiter.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints
    from app.grade import grade
    from app.main import main
    from app.organisation import organisation
    from app.person import person
    from app.practice import practice
    from app.programme import programme
    from app.project import project
    from app.role import role
    from app.team import team

    app.register_blueprint(grade, url_prefix="/v1/organisations")
    app.register_blueprint(organisation, url_prefix="/v1/organisations")
    app.register_blueprint(person, url_prefix="/v1/organisations")
    app.register_blueprint(practice, url_prefix="/v1/organisations")
    app.register_blueprint(programme, url_prefix="/v1/organisations")
    app.register_blueprint(project, url_prefix="/v1/organisations")
    app.register_blueprint(role, url_prefix="/v1/organisations")
    app.register_blueprint(team, url_prefix="/v1/organisations")
    app.register_blueprint(main)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    app.logger.addHandler(stream_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info("Startup")

    return app


from app import models  # noqa: E402, F401
