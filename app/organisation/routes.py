import csv
import json
from datetime import datetime
from io import StringIO

from app import db
from app.models import Organisation
from app.organisation import organisation
from flask import Response, request, url_for
from flask_negotiate import consumes, produces
from jsonschema import FormatChecker, ValidationError, validate
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import BadRequest, Conflict, InternalServerError

# JSON schema for organisation requests
with open("openapi.json") as json_file:
    openapi = json.load(json_file)
organisation_schema = openapi["components"]["schemas"]["OrganisationRequest"]


@organisation.route("", methods=["GET"])
@produces("application/json", "text/csv")
def list():
    """Get a list of Organisations."""
    name_query = request.args.get("name", type=str)

    if name_query:
        organisations = (
            Organisation.query.filter(Organisation.name.ilike(f"%{name_query}%"))
            .order_by(Organisation.name.asc())
            .all()
        )
    else:
        organisations = Organisation.query.order_by(Organisation.name.asc()).all()

    if organisations:
        if "application/json" in request.headers.getlist("accept"):
            results = [organisation.list_item() for organisation in organisations]

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
                w.writerow(("ID", "NAME", "DOMAIN", "CREATED_AT", "UPDATED_AT"))
                yield data.getvalue()
                data.seek(0)
                data.truncate(0)

                # write each item
                for organisation in organisations:
                    w.writerow(
                        (
                            organisation.id,
                            organisation.name,
                            organisation.domain,
                            organisation.created_at.isoformat(),
                            organisation.updated_at.isoformat() if organisation.updated_at else None,
                        )
                    )
                    yield data.getvalue()
                    data.seek(0)
                    data.truncate(0)

            response = Response(generate(), mimetype="text/csv", status=200)
            response.headers.set("Content-Disposition", "attachment", filename="organisations.csv")
            return response
    else:
        return Response(mimetype="application/json", status=204)


@organisation.route("", methods=["POST"])
@consumes("application/json")
@produces("application/json")
def create():
    """Create a new Organisation."""

    # Validate request against schema
    try:
        validate(request.json, organisation_schema, format_checker=FormatChecker())
    except ValidationError as e:
        raise BadRequest(e.message)

    organisation = Organisation(name=request.json["name"], domain=request.json["domain"])

    db.session.add(organisation)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise Conflict()
    except Exception:
        db.session.rollback()
        raise InternalServerError

    response = Response(repr(organisation), mimetype="application/json", status=201)
    response.headers["Location"] = url_for("organisation.get", organisation_id=organisation.id)

    return response


@organisation.route("/<uuid:organisation_id>", methods=["GET"])
@produces("application/json")
def get(organisation_id):
    """Get a specific Organisation."""
    organisation = Organisation.query.get_or_404(str(organisation_id))

    return Response(repr(organisation), mimetype="application/json", status=200)


@organisation.route("/<uuid:organisation_id>", methods=["PUT"])
@consumes("application/json")
@produces("application/json")
def update(organisation_id):
    """Update a specific Organisation."""

    # Validate request against schema
    try:
        validate(request.json, organisation_schema, format_checker=FormatChecker())
    except ValidationError as e:
        raise BadRequest(e.message)

    organisation = Organisation.query.get_or_404(str(organisation_id))

    organisation.name = request.json["name"]
    organisation.domain = request.json["domain"]
    organisation.updated_at = datetime.utcnow()

    db.session.add(organisation)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise Conflict()
    except Exception:
        db.session.rollback()
        raise InternalServerError

    return Response(repr(organisation), mimetype="application/json", status=200)


@organisation.route("/<uuid:organisation_id>", methods=["DELETE"])
@produces("application/json")
def delete(organisation_id):
    """Delete a specific Organisation."""
    organisation = Organisation.query.get_or_404(str(organisation_id))

    db.session.delete(organisation)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise InternalServerError

    return Response(mimetype="application/json", status=204)
