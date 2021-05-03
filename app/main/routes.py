import json

from app.main import bp
from flask import Response
from werkzeug.exceptions import HTTPException, InternalServerError


@bp.route("/openapi", methods=["GET"])
def openapi():
    with open("openapi.json") as openapi_json:
        openapi = json.load(openapi_json)

    return Response(
        json.dumps(openapi, separators=(",", ":")),
        mimetype="application/json",
        status=200,
    )


@bp.app_errorhandler(HTTPException)
def http_error(error):
    return Response(
        response=json.dumps(
            {"code": error.code, "name": error.name, "description": error.description},
            separators=(",", ":"),
        ),
        mimetype="application/json",
        status=error.code,
    )


@bp.app_errorhandler(Exception)
def unhandled_exception(error):
    raise InternalServerError
