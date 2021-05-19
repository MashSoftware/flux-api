import json
from datetime import datetime

from app import db

# from app.models import People
from app.person import person
from flask import Response, request, url_for
from flask_negotiate import consumes, produces
from jsonschema import FormatChecker, ValidationError, validate
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import BadRequest, Conflict, NotImplemented

# JSON schema for organisation requests
with open("openapi.json") as json_file:
    openapi = json.load(json_file)
person_schema = openapi["components"]["schemas"]["PersonRequest"]


@person.route("/<uuid:organisation_id>/people", methods=["GET"])
@produces("application/json")
def list(organisation_id):
    """Get a list of People."""
    return NotImplemented


@person.route("/<uuid:organisation_id>/people", methods=["POST"])
@consumes("application/json")
@produces("application/json")
def create(organisation_id):
    """Create a new People."""
    return NotImplemented


@person.route("/<uuid:organisation_id>/people/<uuid:person_id>", methods=["GET"])
@produces("application/json")
def get(organisation_id, person_id):
    """Get a specific People."""
    return NotImplemented


@person.route("/<uuid:organisation_id>/people/<uuid:person_id>", methods=["PUT"])
@consumes("application/json")
@produces("application/json")
def update(organisation_id, person_id):
    """Update a People with a specific ID."""
    return NotImplemented


@person.route("/<uuid:organisation_id>/people/<uuid:person_id>", methods=["DELETE"])
@produces("application/json")
def delete(organisation_id, person_id):
    """Delete a People with a specific ID."""
    return NotImplemented
