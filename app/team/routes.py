import json
from datetime import datetime

from app import db

# from app.models import Team
from app.team import team
from flask import Response, request, url_for
from flask_negotiate import consumes, produces
from jsonschema import FormatChecker, ValidationError, validate
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import BadRequest, Conflict, NotImplemented

# JSON schema for organisation requests
with open("openapi.json") as json_file:
    openapi = json.load(json_file)
team_schema = openapi["components"]["schemas"]["TeamRequest"]


@team.route("/<uuid:organisation_id>/teams", methods=["GET"])
@produces("application/json")
def list(organisation_id):
    """Get a list of Teams."""
    return NotImplemented


@team.route("/<uuid:organisation_id>/teams", methods=["POST"])
@consumes("application/json")
@produces("application/json")
def create(organisation_id):
    """Create a new Team."""
    return NotImplemented


@team.route("/<uuid:organisation_id>/teams/<uuid:team_id>", methods=["GET"])
@produces("application/json")
def get(organisation_id, team_id):
    """Get a specific Team."""
    return NotImplemented


@team.route("/<uuid:organisation_id>/teams/<uuid:team_id>", methods=["PUT"])
@consumes("application/json")
@produces("application/json")
def update(organisation_id, team_id):
    """Update a Team with a specific ID."""
    return NotImplemented


@team.route("/<uuid:organisation_id>/teams/<uuid:team_id>", methods=["DELETE"])
@produces("application/json")
def delete(organisation_id, team_id):
    """Delete a Team with a specific ID."""
    return NotImplemented
