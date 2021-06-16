import json
from datetime import datetime

from app import db
from app.models import Project
from app.project import project
from flask import Response, request, url_for
from flask_negotiate import consumes, produces
from jsonschema import FormatChecker, ValidationError, validate
from werkzeug.exceptions import BadRequest, InternalServerError

# JSON schema for organisation requests
with open("openapi.json") as json_file:
    openapi = json.load(json_file)
project_schema = openapi["components"]["schemas"]["ProjectRequest"]


@project.route("/<uuid:organisation_id>/projects", methods=["GET"])
@produces("application/json")
def list(organisation_id):
    """Get a list of Projects in an Organisation."""
    name_query = request.args.get("name", type=str)
    programme_filter = request.args.get("programme_id", type=str)
    status_filter = request.args.get("status", type=str)

    if name_query:
        projects = (
            Project.query.filter(Project.name.ilike("%{}%".format(name_query)))
            .filter_by(organisation_id=str(organisation_id))
            .order_by(Project.name.asc())
            .all()
        )
    elif programme_filter:
        projects = (
            Project.query.filter_by(programme_id=programme_filter)
            .filter_by(organisation_id=str(organisation_id))
            .order_by(Project.name.asc())
            .all()
        )
    elif status_filter:
        projects = (
            Project.query.filter_by(status=status_filter)
            .filter_by(organisation_id=str(organisation_id))
            .order_by(Project.name.asc())
            .all()
        )
    else:
        projects = Project.query.filter_by(organisation_id=str(organisation_id)).order_by(Project.name.asc()).all()

    if projects:
        results = []
        for project in projects:
            results.append(project.list_item())

        return Response(
            json.dumps(results, separators=(",", ":")),
            mimetype="application/json",
            status=200,
        )
    else:
        return Response(mimetype="application/json", status=204)


@project.route("/<uuid:organisation_id>/projects", methods=["POST"])
@consumes("application/json")
@produces("application/json")
def create(organisation_id):
    """Create a new Project in an Organisation."""

    # Validate request against schema
    try:
        validate(request.json, project_schema, format_checker=FormatChecker())
    except ValidationError as e:
        raise BadRequest(e.message)

    project = Project(
        name=request.json["name"],
        manager_id=request.json["manager_id"] if "manager_id" in request.json else None,
        programme_id=request.json["programme_id"],
        status=request.json["status"],
        organisation_id=str(organisation_id),
    )

    db.session.add(project)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise InternalServerError

    response = Response(repr(project), mimetype="application/json", status=201)
    response.headers["Location"] = url_for(
        "project.get",
        organisation_id=organisation_id,
        project_id=project.id,
    )

    return response


@project.route("/<uuid:organisation_id>/projects/<uuid:project_id>", methods=["GET"])
@produces("application/json")
def get(organisation_id, project_id):
    """Get a specific Project in an Organisation."""
    project = Project.query.get_or_404(str(project_id))

    return Response(repr(project), mimetype="application/json", status=200)


@project.route("/<uuid:organisation_id>/projects/<uuid:project_id>", methods=["PUT"])
@consumes("application/json")
@produces("application/json")
def update(organisation_id, project_id):
    """Update a Project with a specific ID."""

    # Validate request against schema
    try:
        validate(request.json, project_schema, format_checker=FormatChecker())
    except ValidationError as e:
        raise BadRequest(e.message)

    project = Project.query.get_or_404(str(project_id))

    project.name = request.json["name"]
    project.manager_id = request.json["manager_id"] if "manager_id" in request.json else None
    project.programme_id = request.json["programme_id"]
    project.status = request.json["status"]
    project.updated_at = datetime.utcnow()

    db.session.add(project)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise InternalServerError

    return Response(repr(project), mimetype="application/json", status=200)


@project.route("/<uuid:organisation_id>/projects/<uuid:project_id>", methods=["DELETE"])
@produces("application/json")
def delete(organisation_id, project_id):
    """Delete a Project with a specific ID."""
    project = Project.query.get_or_404(str(project_id))

    db.session.delete(project)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise InternalServerError

    return Response(mimetype="application/json", status=204)
