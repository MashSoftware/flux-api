from flask import Blueprint

role = Blueprint("role", __name__)

from app.role import routes  # noqa: E402, F401
