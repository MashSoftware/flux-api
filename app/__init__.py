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
    from app.organisation import bp as organisation_bp

    app.register_blueprint(organisation_bp, url_prefix="/v1/organisations")

    from app.main import bp as main_bp

    app.register_blueprint(main_bp)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    app.logger.addHandler(stream_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info("Startup")

    return app


from app import models  # noqa: E402, F401
