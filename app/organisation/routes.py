import json
from datetime import datetime

from app import db
from app.models import Organisation, Programme
from app.organisation import bp
from flask import Response, request, url_for
from flask_negotiate import consumes, produces
from jsonschema import FormatChecker, ValidationError, validate
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import BadRequest

# JSON schema for organisation requests
with open("openapi.json") as json_file:
    openapi = json.load(json_file)
organisation_schema = openapi["components"]["schemas"]["OrganisationRequest"]
programme_schema = openapi["components"]["schemas"]["ProgrammeRequest"]


@bp.route("", methods=["GET"])
@produces("application/json")
def get_organisations():
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


@bp.route("", methods=["POST"])
@consumes("application/json")
@produces("application/json")
def create_organisation():
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
    except IntegrityError as e:
        db.session.rollback()
        raise BadRequest()

    response = Response(repr(organisation), mimetype="application/json", status=201)
    response.headers["Location"] = url_for("organisation.get_organisation", organisation_id=organisation.id)

    return response


@bp.route("/<uuid:organisation_id>", methods=["GET"])
@produces("application/json")
def get_organisation(organisation_id):
    """Get a specific Organisation."""
    organisation = Organisation.query.get_or_404(str(organisation_id))

    return Response(repr(organisation), mimetype="application/json", status=200)


@bp.route("/<uuid:organisation_id>", methods=["PUT"])
@consumes("application/json")
@produces("application/json")
def update_organisation(organisation_id):
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
    db.session.commit()

    return Response(repr(organisation), mimetype="application/json", status=200)


@bp.route("/<uuid:organisation_id>", methods=["DELETE"])
@produces("application/json")
def delete_organisation(organisation_id):
    """Delete a specific Organisation."""
    organisation = Organisation.query.get_or_404(str(organisation_id))

    db.session.delete(organisation)
    db.session.commit()

    return Response(mimetype="application/json", status=204)


@bp.route("/<uuid:organisation_id>/programmes", methods=["GET"])
@produces("application/json")
def get_programmes(organisation_id):
    """Get a list of Programmes in an Organisation."""
    name_query = request.args.get("name", type=str)

    if name_query:
        programmes = (
            Programme.query.filter(Programme.name.ilike("%{}%".format(name_query)))
            .filter_by(organisation_id=str(organisation_id))
            .order_by(Programme.created_at.desc())
            .all()
        )
    else:
        programmes = (
            Programme.query.filter_by(organisation_id=str(organisation_id)).order_by(Programme.created_at.desc()).all()
        )

    if programmes:
        results = []
        for programme in programmes:
            results.append(programme.as_dict())

        return Response(
            json.dumps(results, sort_keys=True, separators=(",", ":")),
            mimetype="application/json",
            status=200,
        )
    else:
        return Response(mimetype="application/json", status=204)


@bp.route("/<uuid:organisation_id>/programmes", methods=["POST"])
@consumes("application/json")
@produces("application/json")
def create_programme(organisation_id):
    """Create a new Programme in an Organisation."""

    # Validate request against schema
    try:
        validate(request.json, programme_schema, format_checker=FormatChecker())
    except ValidationError as e:
        raise BadRequest(e.message)

    programme = Programme(name=request.json["name"], organisation_id=str(organisation_id))

    db.session.add(programme)
    db.session.commit()

    response = Response(repr(programme), mimetype="application/json", status=201)
    response.headers["Location"] = url_for(
        "organisation.get_programme",
        organisation_id=organisation_id,
        programme_id=programme.id,
    )

    return response


@bp.route("/<uuid:organisation_id>/programmes/<uuid:programme_id>", methods=["GET"])
@produces("application/json")
def get_programme(organisation_id, programme_id):
    """Get a specific Programme in an Organisation."""
    programme = Programme.query.get_or_404(str(programme_id))

    return Response(repr(programme), mimetype="application/json", status=200)


@bp.route("/<uuid:organisation_id>/programmes/<uuid:programme_id>", methods=["PUT"])
@consumes("application/json")
@produces("application/json")
def update_programme(organisation_id, programme_id):
    """Update a Programme with a specific ID."""

    # Validate request against schema
    try:
        validate(request.json, programme_schema, format_checker=FormatChecker())
    except ValidationError as e:
        raise BadRequest(e.message)

    programme = Programme.query.get_or_404(str(programme_id))

    programme.name = request.json["name"]
    programme.updated_at = datetime.utcnow()

    db.session.add(programme)
    db.session.commit()

    return Response(repr(programme), mimetype="application/json", status=200)


@bp.route("/<uuid:organisation_id>/programmes/<uuid:programme_id>", methods=["DELETE"])
@produces("application/json")
def delete_programme(organisation_id, programme_id):
    """Delete a Programme with a specific ID."""
    programme = Programme.query.get_or_404(str(programme_id))

    db.session.delete(programme)
    db.session.commit()

    return Response(mimetype="application/json", status=204)
