from flask import Blueprint

project = Blueprint("project", __name__)

from app.project import routes  # noqa: E402, F401
