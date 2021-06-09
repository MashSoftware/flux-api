import json
from datetime import datetime

from app import db
from app.models import Organisation, Practice
from app.practice import practice
from flask import Response, request, url_for
from flask_negotiate import consumes, produces
from jsonschema import FormatChecker, ValidationError, validate
from werkzeug.exceptions import BadRequest, InternalServerError

# JSON schema for organisation requests
with open("openapi.json") as json_file:
    openapi = json.load(json_file)
practice_schema = openapi["components"]["schemas"]["PracticeRequest"]


@practice.route("/<uuid:organisation_id>/practices", methods=["GET"])
@produces("application/json")
def list(organisation_id):
    """Get a list of Practices in an Organisation."""
    name_query = request.args.get("name", type=str)

    if name_query:
        practices = (
            Practice.query.filter(Practice.name.ilike("%{}%".format(name_query)))
            .filter_by(organisation_id=str(organisation_id))
            .order_by(Practice.name.asc())
            .all()
        )
    else:
        practices = (
            Practice.query.filter_by(organisation_id=str(organisation_id)).order_by(Practice.name.asc()).all()
        )

    if practices:
        results = []
        for practice in practices:
            results.append(practice.list_item())

        return Response(
            json.dumps(results, separators=(",", ":")),
            mimetype="application/json",
            status=200,
        )
    else:
        return Response(mimetype="application/json", status=204)


@practice.route("/<uuid:organisation_id>/practices", methods=["POST"])
@consumes("application/json")
@produces("application/json")
def create(organisation_id):
    """Create a new Practice in an Organisation."""

    # Validate request against schema
    try:
        validate(request.json, practice_schema, format_checker=FormatChecker())
    except ValidationError as e:
        raise BadRequest(e.message)

    practice = Practice(
        name=request.json["name"],
        head_id=request.json["head_id"] if "head_id" in request.json else None,
        organisation_id=str(organisation_id),
    )

    db.session.add(practice)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise InternalServerError

    response = Response(repr(practice), mimetype="application/json", status=201)
    response.headers["Location"] = url_for(
        "practice.get",
        organisation_id=organisation_id,
        practice_id=practice.id,
    )

    return response


@practice.route("/<uuid:organisation_id>/practices/<uuid:practice_id>", methods=["GET"])
@produces("application/json")
def get(organisation_id, practice_id):
    """Get a specific Practice in an Organisation."""
    practice = Practice.query.get_or_404(str(practice_id))

    return Response(repr(practice), mimetype="application/json", status=200)


@practice.route("/<uuid:organisation_id>/practices/<uuid:practice_id>", methods=["PUT"])
@consumes("application/json")
@produces("application/json")
def update(organisation_id, practice_id):
    """Update a Practice with a specific ID."""
    organisation = Organisation.query.get_or_404(str(organisation_id))

    # Validate request against schema
    try:
        validate(request.json, practice_schema, format_checker=FormatChecker())
    except ValidationError as e:
        raise BadRequest(e.message)

    practice = Practice.query.get_or_404(str(practice_id))

    practice.name = request.json["name"]
    practice.head_id = request.json["head_id"] if "head_id" in request.json else None
    practice.updated_at = datetime.utcnow()

    db.session.add(practice)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise InternalServerError

    return Response(repr(practice), mimetype="application/json", status=200)


@practice.route("/<uuid:organisation_id>/practices/<uuid:practice_id>", methods=["DELETE"])
@produces("application/json")
def delete(organisation_id, practice_id):
    """Delete a Practice with a specific ID."""
    practice = Practice.query.get_or_404(str(practice_id))

    db.session.delete(practice)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise InternalServerError

    return Response(mimetype="application/json", status=204)
