from flask import Blueprint

person = Blueprint("person", __name__)

from app.person import routes  # noqa: E402, F401
