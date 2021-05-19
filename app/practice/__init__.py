from flask import Blueprint

practice = Blueprint("practice", __name__)

from app.practice import routes  # noqa: E402, F401
