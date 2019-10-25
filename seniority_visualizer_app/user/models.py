# -*- coding: utf-8 -*-
"""User models."""
import datetime as dt
from enum import Enum
from typing import Optional, Union

from flask import current_app
from flask_login import UserMixin
from itsdangerous import SignatureExpired, TimedJSONWebSignatureSerializer
from sqlalchemy import func

from seniority_visualizer_app.database import (
    Column,
    Model,
    SurrogatePK,
    db,
    relationship,
)
from seniority_visualizer_app.extensions import bcrypt
from seniority_visualizer_app.user.role import Permissions, Role

from .email import make_email_serializer


class EmailCategories(Enum):
    COMPANY_EMAIL = "company_email"
    PERSONAL_EMAIL = "personal_email"


class User(UserMixin, SurrogatePK, Model):
    """A user of the app."""

    email_categories = EmailCategories

    __tablename__ = "users"
    username = Column(db.String(80), unique=True, nullable=False)
    company_email = Column(db.String(80), unique=True, nullable=False)
    personal_email = Column(db.String(80), unique=True, nullable=False)
    company_email_confirmed = Column(db.Boolean(), default=False)
    personal_email_confirmed = Column(db.Boolean(), default=False)
    #: The hashed password
    password = Column(db.LargeBinary(128), nullable=True)
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    first_name = Column(db.String(30), nullable=True)
    last_name = Column(db.String(30), nullable=True)
    active = Column(db.Boolean(), default=False)
    role_id = Column(db.Integer, db.ForeignKey("roles.id"))
    role = relationship("Role", backref="users")
    employee_id = Column(db.String(16), unique=True, nullable=True)

    def __init__(
            self,
            username,
            company_email,
            personal_email,
            password=None,
            role=None,
            **kwargs,
    ):
        """Create instance."""
        db.Model.__init__(
            self,
            username=username,
            company_email=company_email,
            personal_email=personal_email,
            **kwargs,
        )
        if password:
            self.set_password(password)
        else:
            self.password = None

        if current_app.config.get("FLASK_ADMIN") and (
                current_app.config.get("FLASK_ADMIN") == personal_email.lower()
        ):
            self.role = Role.query.filter(Role.name.ilike("admin")).first()
        else:
            self.role = role or Role.query.filter(Role.default).first()

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

    @property
    def is_admin(self):
        return self.role.has_permission(Permissions.ADMIN)

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

    def generate_confirmation_token(
        self,
        email_category: EmailCategories,
        serializer: Optional[TimedJSONWebSignatureSerializer] = None,
    ) -> bytes:

        if serializer is None:
            serializer = make_email_serializer()

        email_attribute = email_category.value

        if not self.id:
            raise RuntimeError("can not generate token for unsaved user")

        payload = {
            "email": getattr(self, email_attribute),
            "user_id": self.id,
            "email_category": email_attribute,
        }
        token = serializer.dumps(payload)

        return token

    @staticmethod
    def parse_confirmation_token(
            token, serializer: Optional[TimedJSONWebSignatureSerializer] = None
    ) -> Union[dict, bool]:

        if serializer is None:
            serializer = make_email_serializer()

        try:
            payload = serializer.loads(token)
        except SignatureExpired:
            raise
        except Exception as e:
            print(e)
            return False
        else:
            required_keys = {"user_id", "email_category", "email"}
            payload_key_set = set(payload.keys())
            if not payload_key_set.issubset(required_keys):
                return False

            return payload

    def confirm_email(self, email_attr) -> bool:
        """
        Mark the <email_attr>_confirmed as True

        :param email_attr: the name of the email attribute ('company_email' or 'personal_email')
        :raises AttributeError: if 'email_attr' not a valid email attribute
        """
        if email_attr not in [v.value for v in self.email_categories]:
            raise AttributeError(f"{email_attr} not a valid email category")
        attr = f"{email_attr}_confirmed"
        setattr(self, attr, True)
        if email_attr.lower() == "company_email":
            self.role = Role.query.filter(Role.name.ilike("ConfirmedUser")).first()
        self.save()
        return True
