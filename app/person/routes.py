import json
from datetime import datetime

from app import db
from app.models import Person
from app.person import person
from flask import Response, request, url_for
from flask_negotiate import consumes, produces
from jsonschema import FormatChecker, ValidationError, validate
from werkzeug.exceptions import BadRequest, InternalServerError

# JSON schema for organisation requests
with open("openapi.json") as json_file:
    openapi = json.load(json_file)
person_schema = openapi["components"]["schemas"]["PersonRequest"]


@person.route("/<uuid:organisation_id>/people", methods=["GET"])
@produces("application/json")
def list(organisation_id):
    """Get a list of People in an Organisation."""
    name_query = request.args.get("name", type=str)
    role_filter = request.args.get("role_id", type=str)

    if name_query:
        people = (
            Person.query.filter(Person.name.ilike(f"%{name_query}%"))
            .filter_by(organisation_id=str(organisation_id))
            .order_by(Person.name.asc())
            .all()
        )
    elif role_filter:
        people = (
            Person.query.filter_by(role_id=role_filter)
            .filter_by(organisation_id=str(organisation_id))
            .order_by(Person.name.asc())
            .all()
        )
    else:
        people = Person.query.filter_by(organisation_id=str(organisation_id)).order_by(Person.name.asc()).all()

    if people:
        results = []
        for person in people:
            results.append(person.list_item())

        return Response(
            json.dumps(results, separators=(",", ":")),
            mimetype="application/json",
            status=200,
        )
    else:
        return Response(mimetype="application/json", status=204)


@person.route("/<uuid:organisation_id>/people", methods=["POST"])
@consumes("application/json")
@produces("application/json")
def create(organisation_id):
    """Create a new Person in an Organisation."""

    # Validate request against schema
    try:
        validate(request.json, person_schema, format_checker=FormatChecker())
    except ValidationError as e:
        raise BadRequest(e.message)

    person = Person(
        name=request.json["name"],
        email_address=request.json["email_address"],
        full_time_equivalent=request.json["full_time_equivalent"],
        location=request.json["location"],
        employment=request.json["employment"],
        role_id=request.json["role_id"],
        organisation_id=str(organisation_id),
    )

    db.session.add(person)
    db.session.commit()
    # try:
    #     db.session.commit()
    # except Exception:
    #     db.session.rollback()
    #     raise InternalServerError

    response = Response(repr(person), mimetype="application/json", status=201)
    response.headers["Location"] = url_for(
        "person.get",
        organisation_id=organisation_id,
        person_id=person.id,
    )

    return response


@person.route("/<uuid:organisation_id>/people/<uuid:person_id>", methods=["GET"])
@produces("application/json")
def get(organisation_id, person_id):
    """Get a specific Person in an Organisation."""
    person = Person.query.get_or_404(str(person_id))

    return Response(repr(person), mimetype="application/json", status=200)


@person.route("/<uuid:organisation_id>/people/<uuid:person_id>", methods=["PUT"])
@consumes("application/json")
@produces("application/json")
def update(organisation_id, person_id):
    """Update a Person with a specific ID."""

    # Validate request against schema
    try:
        validate(request.json, person_schema, format_checker=FormatChecker())
    except ValidationError as e:
        raise BadRequest(e.message)

    person = Person.query.get_or_404(str(person_id))

    person.name = request.json["name"]
    person.email_address = request.json["email_address"]
    person.full_time_equivalent = request.json["full_time_equivalent"]
    person.location = request.json["location"]
    person.employment = request.json["employment"]
    person.role_id = request.json["role_id"]
    person.updated_at = datetime.utcnow()

    db.session.add(person)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise InternalServerError

    return Response(repr(person), mimetype="application/json", status=200)


@person.route("/<uuid:organisation_id>/people/<uuid:person_id>", methods=["DELETE"])
@produces("application/json")
def delete(organisation_id, person_id):
    """Delete a Person with a specific ID."""
    person = Person.query.get_or_404(str(person_id))

    db.session.delete(person)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise InternalServerError

    return Response(mimetype="application/json", status=204)
