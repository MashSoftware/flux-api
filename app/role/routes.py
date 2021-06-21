import csv
import json
from datetime import datetime
from io import StringIO

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
@produces("application/json", "text/csv")
def list(organisation_id):
    """Get a list of Roles."""
    title_query = request.args.get("title", type=str)
    grade_filter = request.args.get("grade_id", type=str)
    practice_filter = request.args.get("practice_id", type=str)

    if title_query:
        roles = (
            Role.query.filter(Role.title.ilike(f"%{title_query}%"))
            .filter_by(organisation_id=str(organisation_id))
            .order_by(Role.title.asc())
            .all()
        )
    elif grade_filter:
        roles = (
            Role.query.filter_by(grade_id=grade_filter)
            .filter_by(organisation_id=str(organisation_id))
            .order_by(Role.title.asc())
            .all()
        )
    elif practice_filter:
        roles = (
            Role.query.filter_by(practice_id=practice_filter)
            .filter_by(organisation_id=str(organisation_id))
            .order_by(Role.title.asc())
            .all()
        )
    else:
        roles = Role.query.filter_by(organisation_id=str(organisation_id)).order_by(Role.title.asc()).all()

    if roles:
        if "application/json" in request.headers.getlist("accept"):
            results = [role.list_item() for role in roles]

            return Response(
                json.dumps(results, separators=(",", ":")),
                mimetype="application/json",
                status=200,
            )
        elif "text/csv" in request.headers.getlist("accept"):

            def generate():
                data = StringIO()
                w = csv.writer(data)

                # write header
                w.writerow(("ID", "TITLE", "CREATED_AT", "UPDATED_AT"))
                yield data.getvalue()
                data.seek(0)
                data.truncate(0)

                # write each item
                for role in roles:
                    w.writerow(
                        (
                            role.id,
                            role.title,
                            role.created_at.isoformat(),
                            role.updated_at.isoformat() if role.updated_at else None,
                        )
                    )
                    yield data.getvalue()
                    data.seek(0)
                    data.truncate(0)

            response = Response(generate(), mimetype="text/csv", status=200)
            response.headers.set("Content-Disposition", "attachment", filename="roles.csv")
            return response
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

    grade = Grade.query.get(request.json["grade_id"])
    practice = Practice.query.get(request.json["practice_id"]) if "practice_id" in request.json else None
    role = Role(
        title=request.json["title"],
        grade_id=grade.id,
        practice_id=practice.id if practice else None,
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
    role.practice_id = request.json["practice_id"] if "practice_id" in request.json else None
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
