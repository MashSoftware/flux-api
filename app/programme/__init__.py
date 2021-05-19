from flask import Blueprint

programme = Blueprint("programme", __name__)

from app.programme import routes  # noqa: E402, F401
