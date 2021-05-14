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
    programmes = db.relationship("Programme", backref="organisation")
    practices = db.relationship("Practice", backref="organisation")

    # Methods
    def __init__(self, name, domain):
        self.id = str(uuid.uuid4())
        self.name = name
        self.domain = domain.lower()
        self.created_at = datetime.utcnow()

    def __repr__(self):
        return json.dumps(self.as_dict(), sort_keys=True, separators=(",", ":"))

    def as_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "domain": self.domain,
            "grades": len(self.grades),
            "programmes": len(self.programmes),
            "practices": len(self.practices),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


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
        self.name = name
        self.organisation_id = str(uuid.UUID(organisation_id, version=4))
        self.created_at = datetime.utcnow()

    def __repr__(self):
        return json.dumps(self.as_dict(), sort_keys=True, separators=(",", ":"))

    def as_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "organisation": self.organisation.as_dict(),
            "roles": len(self.roles),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Practice(db.Model):
    # Fields
    id = db.Column(UUID, primary_key=True)
    name = db.Column(db.String(), nullable=False, index=True)
    head = db.Column(db.String(), nullable=False, index=True)
    organisation_id = db.Column(UUID, db.ForeignKey("organisation.id", ondelete="CASCADE"), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, index=True)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=True)

    # Relationships
    roles = db.relationship("Role", backref="practice", lazy=True)

    # Methods
    def __init__(self, name, head, organisation_id):
        self.id = str(uuid.uuid4())
        self.name = name
        self.head = head
        self.organisation_id = str(uuid.UUID(organisation_id, version=4))
        self.created_at = datetime.utcnow()

    def __repr__(self):
        return json.dumps(self.as_dict(), sort_keys=True, separators=(",", ":"))

    def as_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "head": self.head,
            "organisation": self.organisation.as_dict(),
            "roles": len(self.roles),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Role(db.Model):
    # Fields
    id = db.Column(UUID, primary_key=True)
    title = db.Column(db.String(), nullable=False, index=True)
    grade_id = db.Column(UUID, db.ForeignKey("grade.id", ondelete="CASCADE"), nullable=False)
    practice_id = db.Column(UUID, db.ForeignKey("practice.id", ondelete="CASCADE"), nullable=False)
    organisation_id = db.Column(UUID, db.ForeignKey("organisation.id", ondelete="CASCADE"), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, index=True)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=True)

    # Relationships
    # employees = db.relationship("Employee", backref="role", lazy=True)

    # Methods
    def __init__(self, title, grade_id, practice_id, organisation_id):
        self.id = str(uuid.uuid4())
        self.title = title
        self.grade_id = grade_id
        self.practice_id = practice_id
        self.organisation_id = str(uuid.UUID(organisation_id, version=4))
        self.created_at = datetime.utcnow()

    def __repr__(self):
        return json.dumps(self.as_dict(), sort_keys=True, separators=(",", ":"))

    def as_dict(self):
        return {
            "id": self.id,
            "title": self.name,
            "grade": self.grade.as_dict(),
            "practice": self.practice.as_dict(),
            "organisation": self.organisation.as_dict(),
            # "employees": len(self.employees),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Programme(db.Model):
    # Fields
    id = db.Column(UUID, primary_key=True)
    name = db.Column(db.String(), nullable=False, index=True)
    programme_manager = db.Column(db.String(), nullable=False, index=True)
    organisation_id = db.Column(UUID, db.ForeignKey("organisation.id", ondelete="CASCADE"), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, index=True)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=True)

    # Relationships
    # projects = db.relationship("Project", backref="programme", lazy=True)

    # Methods
    def __init__(self, name, programme_manager, organisation_id):
        self.id = str(uuid.uuid4())
        self.name = name
        self.programme_manager = programme_manager
        self.organisation_id = str(uuid.UUID(organisation_id, version=4))
        self.created_at = datetime.utcnow()

    def __repr__(self):
        return json.dumps(self.as_dict(), sort_keys=True, separators=(",", ":"))

    def as_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "programme_manager": self.programme_manager,
            "organisation": self.organisation.as_dict(),
            # "projects": len(self.projects),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


# class Project(db.Model):
#     # Fields
#     id = db.Column(UUID, primary_key=True)
#     name = db.Column(db.String(), nullable=False, index=True)
#     code = db.Column(db.String(), nullable=False, index=True)
#     organisation_id = db.Column(UUID, db.ForeignKey("organisation.id"), nullable=False)
#     programme_id = db.Column(UUID, db.ForeignKey("programme.id"), nullable=True)
#     created_at = db.Column(db.DateTime(timezone=True), nullable=False, index=True)
#     updated_at = db.Column(db.DateTime(timezone=True), nullable=True)

#     # Relationships
#     teams = db.relationship("Team", backref="project", lazy=True)
#     # many to many with person


# class Team(db.Model):
#     # Fields
#     id = db.Column(UUID, primary_key=True)
#     name = db.Column(db.String(), nullable=False, index=True)
#     created_at = db.Column(db.DateTime(timezone=True), nullable=False, index=True)
#     updated_at = db.Column(db.DateTime(timezone=True), nullable=True)

#     # Relationships
#     # many to many with person


# class Person(db.Model):
#     # Fields
#     id = db.Column(UUID, primary_key=True)
#     first_name = db.Column(db.String, nullable=False)
#     last_name = db.Column(db.String, nullable=False)
#     job_id = db.Column(
#         UUID, db.ForeignKey("job.id", ondelete="CASCADE"), nullable=False, index=True
#     )
#     organisation_id = db.Column(
#         UUID,
#         db.ForeignKey("organisation.id", ondelete="CASCADE"),
#         nullable=False,
#         index=True,
#     )
#     email_address = db.Column(db.String(254), nullable=False, unique=True)
#     full_time_equivalent = db.Column(db.Float, nullable=True)
#     created_at = db.Column(db.DateTime(timezone=True), nullable=False, index=True)
#     updated_at = db.Column(db.DateTime(timezone=True), nullable=True)

#     # Relationships
#     teams = db.relationship(
#         "Team",
#         secondary=person_team,
#         lazy=True,
#         backref=db.backref("people", lazy=True),
#     )
#     projects = db.relationship(
#         "Project",
#         secondary=person_project,
#         lazy=True,
#         backref=db.backref("people", lazy=True),
#     )

#     # Methods
#     def __init__(
#         self, first_name, last_name, grade_id, job_id, organisation_id, email_address
#     ):
#         self.id = str(uuid.uuid4())
#         self.first_name = first_name.title()
#         self.last_name = last_name.title()
#         self.organisation_id = str(uuid.UUID(organisation_id, version=4))
#         self.job_id = str(uuid.UUID(job_id, version=4))
#         self.email_address = email_address.lower()
#         self.created_at = datetime.utcnow()

#     def __repr__(self):
#         return json.dumps(self.as_dict(), sort_keys=True, separators=(",", ":"))

#     def as_dict(self):
#         return {
#             "id": self.id,
#             "first_name": self.first_name,
#             "last_name": self.last_name,
#             "organisation_id": self.organisation_id,
#             "job_id": self.job_id,
#             "email_address": self.email_address,
#             "full_time_equivalent": self.full_time_equivalent,
#             "created_at": self.created_at.isoformat(),
#             "updated_at": self.updated_at.isoformat() if self.updated_at else None,
#         }
