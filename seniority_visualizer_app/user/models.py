# -*- coding: utf-8 -*-
"""User models."""
import datetime as dt
from typing import Optional

from sqlalchemy import func
from flask_login import UserMixin

from seniority_visualizer_app.database import (
    Column,
    Model,
    SurrogatePK,
    db,
    reference_col,
    relationship,
)
from seniority_visualizer_app.extensions import bcrypt


class Role(SurrogatePK, Model):
    """A role for a user."""

    __tablename__ = "roles"
    name = Column(db.String(80), unique=True, nullable=False)
    user_id = reference_col("users", nullable=True)
    user = relationship("User", backref="roles")

    def __init__(self, name, **kwargs):
        """Create instance."""
        db.Model.__init__(self, name=name, **kwargs)

    def __repr__(self):
        """Represent instance as a unique string."""
        return "<Role({name})>".format(name=self.name)


class User(UserMixin, SurrogatePK, Model):
    """A user of the app."""

    __tablename__ = "users"
    username = Column(db.String(80), unique=True, nullable=False)
    company_email = Column(db.String(80), unique=True, nullable=False)
    personal_email = Column(db.String(80), unique=True, nullable=False)
    #: The hashed password
    password = Column(db.LargeBinary(128), nullable=True)
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    first_name = Column(db.String(30), nullable=True)
    last_name = Column(db.String(30), nullable=True)
    active = Column(db.Boolean(), default=False)
    is_admin = Column(db.Boolean(), default=False)
    # todo: add is_verified feature

    def __init__(
        self, username, company_email, personal_email, password=None, **kwargs
    ):
        """Create instance."""
        db.Model.__init__(
            self,
            username=username,
            company_email=company_email,
            personal_email=personal_email,
            **kwargs
        )
        if password:
            self.set_password(password)
        else:
            self.password = None

    def set_password(self, password):
        """Set password."""
        self.password = bcrypt.generate_password_hash(password)

    def check_password(self, value):
        """Check password."""
        return bcrypt.check_password_hash(self.password, value)

    @property
    def full_name(self):
        """Full user name."""
        return "{0} {1}".format(self.first_name, self.last_name)

    @classmethod
    def get_by_email(
        cls, email_type, query_email: str, case_insensitive=True
    ) -> Optional["User"]:
        """
        Lookup user by email type.

        :param email_type: the actual property, (User.company_email or User.personal_email)
        :param query_email: email to lookup
        :param case_insensitive: ignore case on lookup
        """
        if case_insensitive:
            return cls.query.filter(
                func.lower(email_type) == query_email.lower()
            ).first()
        else:
            return cls.query.filter(email_type == query_email).first()

    def __repr__(self):
        """Represent instance as a unique string."""
        return "<User({username!r})>".format(username=self.username)
