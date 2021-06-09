import json
from datetime import datetime

from app import db
from app.models import Grade
from app.grade import grade
from flask import Response, request, url_for
from flask_negotiate import consumes, produces
from jsonschema import FormatChecker, ValidationError, validate
from werkzeug.exceptions import BadRequest, InternalServerError

# JSON schema for organisation requests
with open("openapi.json") as json_file:
    openapi = json.load(json_file)
grade_schema = openapi["components"]["schemas"]["GradeRequest"]


@grade.route("/<uuid:organisation_id>/grades", methods=["GET"])
@produces("application/json")
def list(organisation_id):
    """Get a list of Grades in an Organisation."""
    name_query = request.args.get("name", type=str)

    if name_query:
        grades = (
            Grade.query.filter(Grade.name.ilike("%{}%".format(name_query)))
            .filter_by(organisation_id=str(organisation_id))
            .order_by(Grade.name.asc())
            .all()
        )
    else:
        grades = Grade.query.filter_by(organisation_id=str(organisation_id)).order_by(Grade.name.asc()).all()

    if grades:
        results = []
        for grade in grades:
            results.append(grade.list_item())

        return Response(
            json.dumps(results, separators=(",", ":")),
            mimetype="application/json",
            status=200,
        )
    else:
        return Response(mimetype="application/json", status=204)


@grade.route("/<uuid:organisation_id>/grades", methods=["POST"])
@consumes("application/json")
@produces("application/json")
def create(organisation_id):
    """Create a new Grade in an Organisation."""

    # Validate request against schema
    try:
        validate(request.json, grade_schema, format_checker=FormatChecker())
    except ValidationError as e:
        raise BadRequest(e.message)

    grade = Grade(
        name=request.json["name"],
        organisation_id=str(organisation_id),
    )

    db.session.add(grade)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise InternalServerError

    response = Response(repr(grade), mimetype="application/json", status=201)
    response.headers["Location"] = url_for(
        "grade.get",
        organisation_id=organisation_id,
        grade_id=grade.id,
    )

    return response


@grade.route("/<uuid:organisation_id>/grades/<uuid:grade_id>", methods=["GET"])
@produces("application/json")
def get(organisation_id, grade_id):
    """Get a specific Grade in an Organisation."""
    grade = Grade.query.get_or_404(str(grade_id))

    return Response(repr(grade), mimetype="application/json", status=200)


@grade.route("/<uuid:organisation_id>/grades/<uuid:grade_id>", methods=["PUT"])
@consumes("application/json")
@produces("application/json")
def update(organisation_id, grade_id):
    """Update a Grade with a specific ID."""

    # Validate request against schema
    try:
        validate(request.json, grade_schema, format_checker=FormatChecker())
    except ValidationError as e:
        raise BadRequest(e.message)

    grade = Grade.query.get_or_404(str(grade_id))

    grade.name = request.json["name"]
    grade.updated_at = datetime.utcnow()

    db.session.add(grade)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise InternalServerError

    return Response(repr(grade), mimetype="application/json", status=200)


@grade.route("/<uuid:organisation_id>/grades/<uuid:grade_id>", methods=["DELETE"])
@produces("application/json")
def delete(organisation_id, grade_id):
    """Delete a Grade with a specific ID."""
    grade = Grade.query.get_or_404(str(grade_id))

    db.session.delete(grade)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise InternalServerError

    return Response(mimetype="application/json", status=204)
