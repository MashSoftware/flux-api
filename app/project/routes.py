import json
from datetime import datetime

from app import db

# from app.models import Project
from app.project import project
from flask import Response, request, url_for
from flask_negotiate import consumes, produces
from jsonschema import FormatChecker, ValidationError, validate
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import BadRequest, Conflict, NotImplemented

# JSON schema for organisation requests
with open("openapi.json") as json_file:
    openapi = json.load(json_file)
project_schema = openapi["components"]["schemas"]["ProjectRequest"]


@project.route("/<uuid:organisation_id>/projects", methods=["GET"])
@produces("application/json")
def list(organisation_id):
    """Get a list of Projects."""
    return NotImplemented


@project.route("/<uuid:organisation_id>/projects", methods=["POST"])
@consumes("application/json")
@produces("application/json")
def create(organisation_id):
    """Create a new Project."""
    return NotImplemented


@project.route("/<uuid:organisation_id>/projects/<uuid:project_id>", methods=["GET"])
@produces("application/json")
def get(organisation_id, project_id):
    """Get a specific Project."""
    return NotImplemented


@project.route("/<uuid:organisation_id>/projects/<uuid:project_id>", methods=["PUT"])
@consumes("application/json")
@produces("application/json")
def update(organisation_id, project_id):
    """Update a Project with a specific ID."""
    return NotImplemented


@project.route("/<uuid:organisation_id>/projects/<uuid:project_id>", methods=["DELETE"])
@produces("application/json")
def delete(organisation_id, project_id):
    """Delete a Project with a specific ID."""
    return NotImplemented
