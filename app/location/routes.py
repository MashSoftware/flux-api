import csv
import json
from datetime import datetime
from io import StringIO

from app import db
from app.location import location
from app.models import Location
from flask import Response, request, url_for
from flask_negotiate import consumes, produces
from jsonschema import FormatChecker, ValidationError, validate
from werkzeug.exceptions import BadRequest, InternalServerError

# JSON schema for organisation requests
with open("openapi.json") as json_file:
    openapi = json.load(json_file)
location_schema = openapi["components"]["schemas"]["LocationRequest"]


@location.route("/<uuid:organisation_id>/locations", methods=["GET"])
@produces("application/json", "text/csv")
def list(organisation_id):
    """Get a list of Locations in an Organisation."""
    name_query = request.args.get("name", type=str)

    if name_query:
        locations = (
            Location.query.filter(Location.name.ilike(f"%{name_query}%"))
            .filter_by(organisation_id=str(organisation_id))
            .order_by(Location.name.asc())
            .all()
        )
    else:
        locations = Location.query.filter_by(organisation_id=str(organisation_id)).order_by(Location.name.asc()).all()

    if locations:
        if "application/json" in request.headers.getlist("accept"):
            results = [location.list_item() for location in locations]

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
                for location in locations:
                    w.writerow(
                        (
                            location.id,
                            location.name,
                            location.created_at.isoformat(),
                            location.updated_at.isoformat() if location.updated_at else None,
                        )
                    )
                    yield data.getvalue()
                    data.seek(0)
                    data.truncate(0)

            response = Response(generate(), mimetype="text/csv", status=200)
            response.headers.set("Content-Disposition", "attachment", filename="locations.csv")
            return response
    else:
        return Response(mimetype="application/json", status=204)


@location.route("/<uuid:organisation_id>/locations", methods=["POST"])
@consumes("application/json")
@produces("application/json")
def create(organisation_id):
    """Create a new Location in an Organisation."""

    # Validate request against schema
    try:
        validate(request.json, location_schema, format_checker=FormatChecker())
    except ValidationError as e:
        raise BadRequest(e.message)

    location = Location(
        name=request.json["name"],
        address=request.json["address"],
        organisation_id=str(organisation_id),
    )

    db.session.add(location)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise InternalServerError

    response = Response(repr(location), mimetype="application/json", status=201)
    response.headers["Location"] = url_for(
        "location.get",
        organisation_id=organisation_id,
        location_id=location.id,
    )

    return response


@location.route("/<uuid:organisation_id>/locations/<uuid:location_id>", methods=["GET"])
@produces("application/json")
def get(organisation_id, location_id):
    """Get a specific Location in an Organisation."""
    location = Location.query.get_or_404(str(location_id))

    return Response(repr(location), mimetype="application/json", status=200)


@location.route("/<uuid:organisation_id>/locations/<uuid:location_id>", methods=["PUT"])
@consumes("application/json")
@produces("application/json")
def update(organisation_id, location_id):
    """Update a Location with a specific ID."""

    # Validate request against schema
    try:
        validate(request.json, location_schema, format_checker=FormatChecker())
    except ValidationError as e:
        raise BadRequest(e.message)

    location = Location.query.get_or_404(str(location_id))

    location.name = request.json["name"]
    location.address = request.json["address"]
    location.updated_at = datetime.utcnow()

    db.session.add(location)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise InternalServerError

    return Response(repr(location), mimetype="application/json", status=200)


@location.route("/<uuid:organisation_id>/locations/<uuid:location_id>", methods=["DELETE"])
@produces("application/json")
def delete(organisation_id, location_id):
    """Delete a Location with a specific ID."""
    location = Location.query.get_or_404(str(location_id))

    db.session.delete(location)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise InternalServerError

    return Response(mimetype="application/json", status=204)
