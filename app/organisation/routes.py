import json
from datetime import datetime

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
@produces("application/json")
def list():
    """Get a list of Organisations."""
    name_query = request.args.get("name", type=str)

    if name_query:
        organisations = (
            Organisation.query.filter(Organisation.name.ilike("%{}%".format(name_query)))
            .order_by(Organisation.created_at.desc())
            .all()
        )
    else:
        organisations = Organisation.query.order_by(Organisation.created_at.desc()).all()

    if organisations:
        results = []
        for organisation in organisations:
            results.append(organisation.as_dict())

        return Response(
            json.dumps(results, sort_keys=True, separators=(",", ":")),
            mimetype="application/json",
            status=200,
        )
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
