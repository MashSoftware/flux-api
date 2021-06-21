import csv
import json
from datetime import datetime
from io import StringIO

from app import db
from app.models import Programme
from app.programme import programme
from flask import Response, request, url_for
from flask_negotiate import consumes, produces
from jsonschema import FormatChecker, ValidationError, validate
from werkzeug.exceptions import BadRequest, InternalServerError

# JSON schema for organisation requests
with open("openapi.json") as json_file:
    openapi = json.load(json_file)
programme_schema = openapi["components"]["schemas"]["ProgrammeRequest"]


@programme.route("/<uuid:organisation_id>/programmes", methods=["GET"])
@produces("application/json", "text/csv")
def list(organisation_id):
    """Get a list of Programmes in an Organisation."""
    name_query = request.args.get("name", type=str)

    if name_query:
        programmes = (
            Programme.query.filter(Programme.name.ilike(f"%{name_query}%"))
            .filter_by(organisation_id=str(organisation_id))
            .order_by(Programme.name.asc())
            .all()
        )
    else:
        programmes = (
            Programme.query.filter_by(organisation_id=str(organisation_id)).order_by(Programme.name.asc()).all()
        )

    if programmes:
        if "application/json" in request.headers.getlist("accept"):
            results = [programme.list_item() for programme in programmes]

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
                w.writerow(("ID", "NAME", "CREATED_AT", "UPDATED_AT"))
                yield data.getvalue()
                data.seek(0)
                data.truncate(0)

                # write each item
                for programme in programmes:
                    w.writerow(
                        (
                            programme.id,
                            programme.name,
                            programme.created_at.isoformat(),
                            programme.updated_at.isoformat() if programme.updated_at else None,
                        )
                    )
                    yield data.getvalue()
                    data.seek(0)
                    data.truncate(0)

            response = Response(generate(), mimetype="text/csv", status=200)
            response.headers.set("Content-Disposition", "attachment", filename="programmes.csv")
            return response
    else:
        return Response(mimetype="application/json", status=204)


@programme.route("/<uuid:organisation_id>/programmes", methods=["POST"])
@consumes("application/json")
@produces("application/json")
def create(organisation_id):
    """Create a new Programme in an Organisation."""

    # Validate request against schema
    try:
        validate(request.json, programme_schema, format_checker=FormatChecker())
    except ValidationError as e:
        raise BadRequest(e.message)

    programme = Programme(
        name=request.json["name"],
        manager_id=request.json["manager_id"] if "manager_id" in request.json else None,
        organisation_id=str(organisation_id),
    )

    db.session.add(programme)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise InternalServerError

    response = Response(repr(programme), mimetype="application/json", status=201)
    response.headers["Location"] = url_for(
        "programme.get",
        organisation_id=organisation_id,
        programme_id=programme.id,
    )

    return response


@programme.route("/<uuid:organisation_id>/programmes/<uuid:programme_id>", methods=["GET"])
@produces("application/json")
def get(organisation_id, programme_id):
    """Get a specific Programme in an Organisation."""
    programme = Programme.query.get_or_404(str(programme_id))

    return Response(repr(programme), mimetype="application/json", status=200)


@programme.route("/<uuid:organisation_id>/programmes/<uuid:programme_id>", methods=["PUT"])
@consumes("application/json")
@produces("application/json")
def update(organisation_id, programme_id):
    """Update a Programme with a specific ID."""

    # Validate request against schema
    try:
        validate(request.json, programme_schema, format_checker=FormatChecker())
    except ValidationError as e:
        raise BadRequest(e.message)

    programme = Programme.query.get_or_404(str(programme_id))

    programme.name = request.json["name"]
    programme.manager_id = request.json["manager_id"] if "manager_id" in request.json else None
    programme.updated_at = datetime.utcnow()

    db.session.add(programme)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise InternalServerError

    return Response(repr(programme), mimetype="application/json", status=200)


@programme.route("/<uuid:organisation_id>/programmes/<uuid:programme_id>", methods=["DELETE"])
@produces("application/json")
def delete(organisation_id, programme_id):
    """Delete a Programme with a specific ID."""
    programme = Programme.query.get_or_404(str(programme_id))

    db.session.delete(programme)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise InternalServerError

    return Response(mimetype="application/json", status=204)
