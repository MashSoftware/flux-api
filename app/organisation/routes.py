import json
from datetime import datetime

from app import db
from app.models import Grade, Organisation, Practice, Programme, Role
from app.organisation import bp
from flask import Response, request, url_for
from flask_negotiate import consumes, produces
from jsonschema import FormatChecker, ValidationError, validate
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import BadRequest, Conflict

# JSON schema for organisation requests
with open("openapi.json") as json_file:
    openapi = json.load(json_file)
organisation_schema = openapi["components"]["schemas"]["OrganisationRequest"]
programme_schema = openapi["components"]["schemas"]["ProgrammeRequest"]
grade_schema = openapi["components"]["schemas"]["GradeRequest"]
practice_schema = openapi["components"]["schemas"]["PracticeRequest"]
role_schema = openapi["components"]["schemas"]["RoleRequest"]


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
    except IntegrityError:
        db.session.rollback()
        raise Conflict()

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

    programme = Programme(
        name=request.json["name"],
        programme_manager=request.json["programme_manager"],
        organisation_id=str(organisation_id),
    )

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
    programme.programme_manager = request.json["programme_manager"]
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


@bp.route("/<uuid:organisation_id>/grades", methods=["GET"])
@produces("application/json")
def get_grades(organisation_id):
    """Get a list of Grades in an Organisation."""
    name_query = request.args.get("name", type=str)

    if name_query:
        grades = (
            Grade.query.filter(Grade.name.ilike("%{}%".format(name_query)))
            .filter_by(organisation_id=str(organisation_id))
            .order_by(Grade.created_at.desc())
            .all()
        )
    else:
        grades = Grade.query.filter_by(organisation_id=str(organisation_id)).order_by(Grade.created_at.desc()).all()

    if grades:
        results = []
        for grade in grades:
            results.append(grade.as_dict())

        return Response(
            json.dumps(results, sort_keys=True, separators=(",", ":")),
            mimetype="application/json",
            status=200,
        )
    else:
        return Response(mimetype="application/json", status=204)


@bp.route("/<uuid:organisation_id>/grades", methods=["POST"])
@consumes("application/json")
@produces("application/json")
def create_grade(organisation_id):
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
    db.session.commit()

    response = Response(repr(grade), mimetype="application/json", status=201)
    response.headers["Location"] = url_for(
        "organisation.get_grade",
        organisation_id=organisation_id,
        grade_id=grade.id,
    )

    return response


@bp.route("/<uuid:organisation_id>/grades/<uuid:grade_id>", methods=["GET"])
@produces("application/json")
def get_grade(organisation_id, grade_id):
    """Get a specific Grade in an Organisation."""
    grade = Grade.query.get_or_404(str(grade_id))

    return Response(repr(grade), mimetype="application/json", status=200)


@bp.route("/<uuid:organisation_id>/grades/<uuid:grade_id>", methods=["PUT"])
@consumes("application/json")
@produces("application/json")
def update_grade(organisation_id, grade_id):
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
    db.session.commit()

    return Response(repr(grade), mimetype="application/json", status=200)


@bp.route("/<uuid:organisation_id>/grades/<uuid:grade_id>", methods=["DELETE"])
@produces("application/json")
def delete_grade(organisation_id, grade_id):
    """Delete a Grade with a specific ID."""
    grade = Grade.query.get_or_404(str(grade_id))

    db.session.delete(grade)
    db.session.commit()

    return Response(mimetype="application/json", status=204)


@bp.route("/<uuid:organisation_id>/practices", methods=["GET"])
@produces("application/json")
def get_practices(organisation_id):
    """Get a list of Practices in an Organisation."""
    name_query = request.args.get("name", type=str)

    if name_query:
        practices = (
            Practice.query.filter(Practice.name.ilike("%{}%".format(name_query)))
            .filter_by(organisation_id=str(organisation_id))
            .order_by(Practice.created_at.desc())
            .all()
        )
    else:
        practices = (
            Practice.query.filter_by(organisation_id=str(organisation_id)).order_by(Practice.created_at.desc()).all()
        )

    if practices:
        results = []
        for practice in practices:
            results.append(practice.as_dict())

        return Response(
            json.dumps(results, sort_keys=True, separators=(",", ":")),
            mimetype="application/json",
            status=200,
        )
    else:
        return Response(mimetype="application/json", status=204)


@bp.route("/<uuid:organisation_id>/practices", methods=["POST"])
@consumes("application/json")
@produces("application/json")
def create_practice(organisation_id):
    """Create a new Practice in an Organisation."""

    # Validate request against schema
    try:
        validate(request.json, practice_schema, format_checker=FormatChecker())
    except ValidationError as e:
        raise BadRequest(e.message)

    practice = Practice(
        name=request.json["name"],
        head=request.json["head"],
        organisation_id=str(organisation_id),
    )

    db.session.add(practice)
    db.session.commit()

    response = Response(repr(practice), mimetype="application/json", status=201)
    response.headers["Location"] = url_for(
        "organisation.get_practice",
        organisation_id=organisation_id,
        practice_id=practice.id,
    )

    return response


@bp.route("/<uuid:organisation_id>/practices/<uuid:practice_id>", methods=["GET"])
@produces("application/json")
def get_practice(organisation_id, practice_id):
    """Get a specific Practice in an Organisation."""
    practice = Practice.query.get_or_404(str(practice_id))

    return Response(repr(practice), mimetype="application/json", status=200)


@bp.route("/<uuid:organisation_id>/practices/<uuid:practice_id>", methods=["PUT"])
@consumes("application/json")
@produces("application/json")
def update_practice(organisation_id, practice_id):
    """Update a Practice with a specific ID."""

    # Validate request against schema
    try:
        validate(request.json, practice_schema, format_checker=FormatChecker())
    except ValidationError as e:
        raise BadRequest(e.message)

    practice = Practice.query.get_or_404(str(practice_id))

    practice.name = request.json["name"]
    practice.head = request.json["head"]
    practice.updated_at = datetime.utcnow()

    db.session.add(practice)
    db.session.commit()

    return Response(repr(practice), mimetype="application/json", status=200)


@bp.route("/<uuid:organisation_id>/practices/<uuid:practice_id>", methods=["DELETE"])
@produces("application/json")
def delete_practice(organisation_id, practice_id):
    """Delete a Practice with a specific ID."""
    practice = Practice.query.get_or_404(str(practice_id))

    db.session.delete(practice)
    db.session.commit()

    return Response(mimetype="application/json", status=204)


@bp.route("/<uuid:organisation_id>/practices/<uuid:practice_id>/roles", methods=["GET"])
@produces("application/json")
def get_roles(organisation_id, practice_id):
    """Get a list of Roles in an Practice."""
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
            results.append(role.as_dict())

        return Response(
            json.dumps(results, sort_keys=True, separators=(",", ":")),
            mimetype="application/json",
            status=200,
        )
    else:
        return Response(mimetype="application/json", status=204)


@bp.route("/<uuid:organisation_id>/practices/<uuid:practice_id>/roles", methods=["POST"])
@consumes("application/json")
@produces("application/json")
def create_role(organisation_id, practice_id):
    """Create a new Role in an Practice."""

    # Validate request against schema
    try:
        validate(request.json, role_schema, format_checker=FormatChecker())
    except ValidationError as e:
        raise BadRequest(e.message)

    role = Role(
        name=request.json["name"],
        head=request.json["head"],
        organisation_id=str(organisation_id),
    )

    db.session.add(role)
    db.session.commit()

    response = Response(repr(role), mimetype="application/json", status=201)
    response.headers["Location"] = url_for(
        "organisation.get_role",
        organisation_id=organisation_id,
        role_id=role.id,
    )

    return response


@bp.route("/<uuid:organisation_id>/practices/<uuid:practice_id>/roles/<uuid:role_id>", methods=["GET"])
@produces("application/json")
def get_role(organisation_id, practice_id, role_id):
    """Get a specific Role in an Practice."""
    role = Role.query.get_or_404(str(role_id))

    return Response(repr(role), mimetype="application/json", status=200)


@bp.route("/<uuid:organisation_id>/practices/<uuid:practice_id>/roles/<uuid:role_id>", methods=["PUT"])
@consumes("application/json")
@produces("application/json")
def update_role(organisation_id, practice_id, role_id):
    """Update a Role with a specific ID."""

    # Validate request against schema
    try:
        validate(request.json, role_schema, format_checker=FormatChecker())
    except ValidationError as e:
        raise BadRequest(e.message)

    role = Role.query.get_or_404(str(role_id))

    role.name = request.json["name"]
    role.head = request.json["head"]
    role.updated_at = datetime.utcnow()

    db.session.add(role)
    db.session.commit()

    return Response(repr(role), mimetype="application/json", status=200)


@bp.route("/<uuid:organisation_id>/practices/<uuid:practice_id>/roles/<uuid:role_id>", methods=["DELETE"])
@produces("application/json")
def delete_role(organisation_id, practice_id, role_id):
    """Delete a Role with a specific ID."""
    role = Role.query.get_or_404(str(role_id))

    db.session.delete(role)
    db.session.commit()

    return Response(mimetype="application/json", status=204)
