from flask import Blueprint

location = Blueprint("location", __name__)

from app.location import routes  # noqa: E402, F401
