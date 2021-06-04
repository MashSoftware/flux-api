import json
from datetime import datetime

from app import db
from app.models import Grade, Practice, Role
from app.role import role
from flask import Response, request, url_for
from flask_negotiate import consumes, produces
from jsonschema import FormatChecker, ValidationError, validate
from werkzeug.exceptions import BadRequest, InternalServerError

# JSON schema for organisation requests
with open("openapi.json") as json_file:
    openapi = json.load(json_file)
role_schema = openapi["components"]["schemas"]["RoleRequest"]


@role.route("/<uuid:organisation_id>/roles", methods=["GET"])
@produces("application/json")
def list(organisation_id):
    """Get a list of Roles."""
    name_query = request.args.get("name", type=str)

    if name_query:
        roles = (
            Role.query.filter(Role.name.ilike("%{}%".format(name_query)))
            .filter_by(organisation_id=str(organisation_id))
            .order_by(Role.created_at.desc())
            .all()
        )
    else:
        roles = Role.query.filter_by(organisation_id=str(organisation_id)).order_by(Role.created_at.desc()).all()

    if roles:
        results = []
        for role in roles:
            results.append(role.list_item())

        return Response(
            json.dumps(results, sort_keys=True, separators=(",", ":")),
            mimetype="application/json",
            status=200,
        )
    else:
        return Response(mimetype="application/json", status=204)


@role.route("/<uuid:organisation_id>/roles", methods=["POST"])
@consumes("application/json")
@produces("application/json")
def create(organisation_id):
    """Create a new Role."""

    # Validate request against schema
    try:
        validate(request.json, role_schema, format_checker=FormatChecker())
    except ValidationError as e:
        raise BadRequest(e.message)

    grade = Grade.query.get_or_404(request.json["grade_id"], description="Grade not found")
    practice = Practice.query.get_or_404(request.json["practice_id"], description="Practice not found")
    role = Role(
        title=request.json["title"],
        grade_id=request.json["grade_id"],
        practice_id=request.json["practice_id"],
        organisation_id=str(organisation_id),
    )

    db.session.add(role)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise InternalServerError

    response = Response(repr(role), mimetype="application/json", status=201)
    response.headers["Location"] = url_for(
        "role.get",
        organisation_id=organisation_id,
        role_id=role.id,
    )

    return response


@role.route("/<uuid:organisation_id>/roles/<uuid:role_id>", methods=["GET"])
@produces("application/json")
def get(organisation_id, role_id):
    """Get a specific Role."""
    role = Role.query.get_or_404(str(role_id))

    return Response(repr(role), mimetype="application/json", status=200)


@role.route("/<uuid:organisation_id>/roles/<uuid:role_id>", methods=["PUT"])
@consumes("application/json")
@produces("application/json")
def update(organisation_id, role_id):
    """Update a Role with a specific ID."""

    # Validate request against schema
    try:
        validate(request.json, role_schema, format_checker=FormatChecker())
    except ValidationError as e:
        raise BadRequest(e.message)

    role = Role.query.get_or_404(str(role_id))

    role.title = request.json["title"]
    role.grade_id = request.json["grade_id"]
    role.practice_id = request.json["practice_id"]
    role.updated_at = datetime.utcnow()

    db.session.add(role)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise InternalServerError

    return Response(repr(role), mimetype="application/json", status=200)


@role.route("/<uuid:organisation_id>/roles/<uuid:role_id>", methods=["DELETE"])
@produces("application/json")
def delete(organisation_id, role_id):
    """Delete a Role with a specific ID."""
    role = Role.query.get_or_404(str(role_id))

    db.session.delete(role)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise InternalServerError

    return Response(mimetype="application/json", status=204)
