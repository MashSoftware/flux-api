import json
import uuid
from datetime import datetime

from sqlalchemy.dialects.postgresql import UUID

from app import db

# person_team = db.Table(
#     "person_team",
#     db.Column(
#         "person_id",
#         UUID,
#         db.ForeignKey("person.id", ondelete="CASCADE"),
#         primary_key=True,
#     ),
#     db.Column(
#         "team_id", UUID, db.ForeignKey("team.id", ondelete="CASCADE"), primary_key=True
#     ),
#     db.Index("ix_person_team_person_id_team_id", "team_id", "person_id", unique=True),
# )

# person_project = db.Table(
#     "person_project",
#     db.Column(
#         "person_id",
#         UUID,
#         db.ForeignKey("person.id", ondelete="CASCADE"),
#         primary_key=True,
#     ),
#     db.Column(
#         "project_id",
#         UUID,
#         db.ForeignKey("project.id", ondelete="CASCADE"),
#         primary_key=True,
#     ),
#     db.Index(
#         "ix_person_project_person_id_project_id", "project_id", "person_id", unique=True
#     ),
# )


class Organisation(db.Model):
    # Fields
    id = db.Column(UUID, primary_key=True)
    name = db.Column(db.String(), nullable=False, index=True)  # Should this be unique too, or just domain?
    domain = db.Column(db.String(), nullable=False, index=True, unique=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, index=True)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=True)

    # Relationships
    grades = db.relationship("Grade", backref="organisation")
    locations = db.relationship("Location", backref="organisation")
    people = db.relationship("Person", backref="organisation")
    practices = db.relationship("Practice", backref="organisation")
    programmes = db.relationship("Programme", backref="organisation")
    projects = db.relationship("Project", backref="organisation")
    roles = db.relationship("Role", backref="organisation")

    # Methods
    def __init__(self, name, domain):
        self.id = str(uuid.uuid4())
        self.name = name.strip()
        self.domain = domain.strip().lower()
        self.created_at = datetime.utcnow()

    def __repr__(self):
        return json.dumps(self.as_dict(), separators=(",", ":"))

    def as_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "domain": self.domain,
            "grades": len(self.grades),
            "locations": len(self.locations),
            "people": len(self.people),
            "practices": len(self.practices),
            "programmes": len(self.programmes),
            "projects": len(self.projects),
            "roles": len(self.roles),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def list_item(self):
        return {
            "id": self.id,
            "name": self.name,
            "domain": self.domain,
        }


class Location(db.Model):
    # Fields
    id = db.Column(UUID, primary_key=True)
    name = db.Column(db.String(), nullable=False, index=True)
    address = db.Column(db.String(), nullable=False)
    organisation_id = db.Column(UUID, db.ForeignKey("organisation.id", ondelete="CASCADE"), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, index=True)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=True)

    # Relationships
    people = db.relationship("Person", backref="location", lazy=True)

    # Methods
    def __init__(self, name, address, organisation_id):
        self.id = str(uuid.uuid4())
        self.name = name.strip().title()
        self.address = address.strip()
        self.organisation_id = str(uuid.UUID(organisation_id, version=4))
        self.created_at = datetime.utcnow()

    def __repr__(self):
        return json.dumps(self.as_dict(), separators=(",", ":"))

    def as_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "address": self.address,
            "organisation": {
                "id": self.organisation.id,
                "name": self.organisation.name,
            },
            "people": len(self.people),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def list_item(self):
        return {"id": self.id, "name": self.name}


class Grade(db.Model):
    # Fields
    id = db.Column(UUID, primary_key=True)
    name = db.Column(db.String(), nullable=False, index=True)
    organisation_id = db.Column(UUID, db.ForeignKey("organisation.id", ondelete="CASCADE"), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, index=True)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=True)

    # Relationships
    roles = db.relationship("Role", backref="grade", lazy=True)

    # Methods
    def __init__(self, name, organisation_id):
        self.id = str(uuid.uuid4())
        self.name = name.strip()
        self.organisation_id = str(uuid.UUID(organisation_id, version=4))
        self.created_at = datetime.utcnow()

    def __repr__(self):
        return json.dumps(self.as_dict(), separators=(",", ":"))

    def as_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "organisation": {
                "id": self.organisation.id,
                "name": self.organisation.name,
            },
            "roles": len(self.roles),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def list_item(self):
        return {"id": self.id, "name": self.name}


class Practice(db.Model):
    # Fields
    id = db.Column(UUID, primary_key=True)
    name = db.Column(db.String(), nullable=False, index=True)
    head_id = db.Column(UUID, db.ForeignKey("person.id", ondelete="SET NULL"), nullable=True, index=True)
    cost_centre = db.Column(db.String(), nullable=True)
    organisation_id = db.Column(UUID, db.ForeignKey("organisation.id", ondelete="CASCADE"), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, index=True)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=True)

    # Relationships
    head = db.relationship("Person", uselist=False)
    roles = db.relationship("Role", backref="practice", lazy=True)

    # Methods
    def __init__(self, name, head_id, cost_centre, organisation_id):
        self.id = str(uuid.uuid4())
        self.name = name.strip().title()
        self.head_id = str(uuid.UUID(head_id, version=4)) if head_id else None
        self.cost_centre = cost_centre.strip() if cost_centre else None
        self.organisation_id = str(uuid.UUID(organisation_id, version=4))
        self.created_at = datetime.utcnow()

    def __repr__(self):
        return json.dumps(self.as_dict(), separators=(",", ":"))

    def as_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "head": {
                "id": self.head.id,
                "name": self.head.name,
            }
            if self.head
            else None,
            "cost_centre": self.cost_centre,
            "organisation": {
                "id": self.organisation.id,
                "name": self.organisation.name,
            },
            "roles": len(self.roles),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def list_item(self):
        return {
            "id": self.id,
            "name": self.name,
            "head": {
                "id": self.head.id,
                "name": self.head.name,
            }
            if self.head
            else None,
        }


class Role(db.Model):
    # Fields
    id = db.Column(UUID, primary_key=True)
    title = db.Column(db.String(), nullable=False, index=True)
    grade_id = db.Column(UUID, db.ForeignKey("grade.id", ondelete="CASCADE"), nullable=False)
    practice_id = db.Column(UUID, db.ForeignKey("practice.id", ondelete="CASCADE"), nullable=True)
    organisation_id = db.Column(UUID, db.ForeignKey("organisation.id", ondelete="CASCADE"), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, index=True)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=True)

    # Relationships
    people = db.relationship("Person", backref="role", lazy=True)

    # Methods
    def __init__(self, title, grade_id, practice_id, organisation_id):
        self.id = str(uuid.uuid4())
        self.title = title.strip()
        self.grade_id = str(uuid.UUID(grade_id, version=4))
        self.practice_id = str(uuid.UUID(practice_id, version=4)) if practice_id else None
        self.organisation_id = str(uuid.UUID(organisation_id, version=4))
        self.created_at = datetime.utcnow()

    def __repr__(self):
        return json.dumps(self.as_dict(), separators=(",", ":"))

    def as_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "grade": {"id": self.grade.id, "name": self.grade.name},
            "practice": self.practice.list_item() if self.practice else None,
            "organisation": {
                "id": self.organisation.id,
                "name": self.organisation.name,
            },
            "people": len(self.people),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def list_item(self):
        return {
            "id": self.id,
            "title": self.title,
            "grade": self.grade.list_item(),
            "practice": {"id": self.practice.id, "name": self.practice.name} if self.practice else None,
        }


class Person(db.Model):
    # Fields
    id = db.Column(UUID, primary_key=True)
    name = db.Column(db.String, nullable=False)
    role_id = db.Column(UUID, db.ForeignKey("role.id", ondelete="CASCADE"), nullable=False, index=True)
    organisation_id = db.Column(
        UUID,
        db.ForeignKey("organisation.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    email_address = db.Column(db.String(254), nullable=False, unique=True)
    full_time_equivalent = db.Column(db.Float, nullable=True)
    location_id = db.Column(
        UUID,
        db.ForeignKey("location.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    employment = db.Column(db.String, nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, index=True)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=True)

    # Relationships
    # teams = db.relationship(
    #     "Team",
    #     secondary=person_team,
    #     lazy=True,
    #     backref=db.backref("people", lazy=True),
    # )
    # projects = db.relationship(
    #     "Project",
    #     secondary=person_project,
    #     lazy=True,
    #     backref=db.backref("people", lazy=True),
    # )

    # Methods
    def __init__(
        self,
        name,
        role_id,
        organisation_id,
        email_address,
        full_time_equivalent,
        location_id,
        employment,
    ):
        self.id = str(uuid.uuid4())
        self.name = name.strip().title()
        self.organisation_id = str(uuid.UUID(organisation_id, version=4))
        self.role_id = str(uuid.UUID(role_id, version=4))
        self.email_address = email_address.strip().lower()
        self.full_time_equivalent = full_time_equivalent.strip()
        self.location_id = str(uuid.UUID(location_id, version=4))
        self.employment = employment.strip()
        self.created_at = datetime.utcnow()

    def __repr__(self):
        return json.dumps(self.as_dict(), separators=(",", ":"))

    def as_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "organisation": {
                "id": self.organisation.id,
                "name": self.organisation.name,
            },
            "role": self.role.list_item(),
            "email_address": self.email_address,
            "full_time_equivalent": self.full_time_equivalent,
            "location": self.location.list_item(),
            "employment": self.employment,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def list_item(self):
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role.list_item(),
            "location": self.location.list_item(),
        }


class Programme(db.Model):
    # Fields
    id = db.Column(UUID, primary_key=True)
    name = db.Column(db.String(), nullable=False, index=True)
    manager_id = db.Column(UUID, db.ForeignKey("person.id", ondelete="SET NULL"), nullable=True, index=True)
    organisation_id = db.Column(UUID, db.ForeignKey("organisation.id", ondelete="CASCADE"), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, index=True)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=True)

    # Relationships
    manager = db.relationship("Person", uselist=False)
    projects = db.relationship("Project", backref="programme", lazy=True)

    # Methods
    def __init__(self, name, manager_id, organisation_id):
        self.id = str(uuid.uuid4())
        self.name = name.strip()
        self.manager_id = str(uuid.UUID(manager_id, version=4)) if manager_id else None
        self.organisation_id = str(uuid.UUID(organisation_id, version=4))
        self.created_at = datetime.utcnow()

    def __repr__(self):
        return json.dumps(self.as_dict(), separators=(",", ":"))

    def as_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "manager": {
                "id": self.manager.id,
                "name": self.manager.name,
            }
            if self.manager
            else None,
            "organisation": {
                "id": self.organisation.id,
                "name": self.organisation.name,
            },
            "projects": len(self.projects),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def list_item(self):
        return {
            "id": self.id,
            "name": self.name,
            "manager": {
                "id": self.manager.id,
                "name": self.manager.name,
            }
            if self.manager
            else None,
        }


class Project(db.Model):
    # Fields
    id = db.Column(UUID, primary_key=True)
    name = db.Column(db.String(), nullable=False, index=True)
    manager_id = db.Column(UUID, db.ForeignKey("person.id", ondelete="SET NULL"), nullable=True, index=True)
    programme_id = db.Column(UUID, db.ForeignKey("programme.id"), nullable=True)
    status = db.Column(db.String(), nullable=False, index=True)
    organisation_id = db.Column(UUID, db.ForeignKey("organisation.id"), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, index=True)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=True)

    # Relationships
    manager = db.relationship("Person", uselist=False)
    # teams = db.relationship("Team", backref="project", lazy=True)
    # many to many with person

    # Methods
    def __init__(self, name, manager_id, programme_id, status, organisation_id):
        self.id = str(uuid.uuid4())
        self.name = name.strip()
        self.manager_id = str(uuid.UUID(manager_id, version=4)) if manager_id else None
        self.programme_id = str(uuid.UUID(programme_id, version=4))
        self.status = status.strip()
        self.organisation_id = str(uuid.UUID(organisation_id, version=4))
        self.created_at = datetime.utcnow()

    def __repr__(self):
        return json.dumps(self.as_dict(), separators=(",", ":"))

    def as_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "manager": {
                "id": self.manager.id,
                "name": self.manager.name,
            }
            if self.manager
            else None,
            "programme": {
                "id": self.programme.id,
                "name": self.programme.name,
            },
            "status": self.status,
            "organisation": {
                "id": self.organisation.id,
                "name": self.organisation.name,
            },
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def list_item(self):
        return {
            "id": self.id,
            "name": self.name,
            "manager": {
                "id": self.manager.id,
                "name": self.manager.name,
            }
            if self.manager
            else None,
            "programme": {
                "id": self.programme.id,
                "name": self.programme.name,
            },
            "status": self.status,
        }


# class Team(db.Model):
#     # Fields
#     id = db.Column(UUID, primary_key=True)
#     name = db.Column(db.String(), nullable=False, index=True)
#     created_at = db.Column(db.DateTime(timezone=True), nullable=False, index=True)
#     updated_at = db.Column(db.DateTime(timezone=True), nullable=True)

#     # Relationships
#     # many to many with person
