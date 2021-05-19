from flask import Blueprint

organisation = Blueprint("organisation", __name__, url_prefix="/v1/organisations")

from app.organisation import routes  # noqa: E402, F401
