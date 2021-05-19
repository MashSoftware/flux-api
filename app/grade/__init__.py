from flask import Blueprint

grade = Blueprint("grade", __name__)

from app.grade import routes  # noqa: E402, F401
