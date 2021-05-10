from flask import Blueprint

bp = Blueprint("organisation", __name__)

from app.organisation import routes  # noqa: E402, F401
