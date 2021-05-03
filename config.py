import os


class Config(object):
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("DATABASE_URL").replace("postgres://", "postgresql://")
        if os.environ.get("DATABASE_URL")
        else "postgresql://mash:mash@localhost:5432/thing"
    )
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_size": 20}
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    RATELIMIT_STORAGE_URL = os.environ.get("REDIS_URL") or "memory://"
    RATELIMIT_HEADERS_ENABLED = True
