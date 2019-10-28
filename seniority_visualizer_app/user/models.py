# -*- coding: utf-8 -*-
"""User models."""
import datetime as dt
from enum import Enum
from typing import Optional, Union, Any

from flask import current_app
from flask_login import UserMixin
from itsdangerous import SignatureExpired, TimedJSONWebSignatureSerializer
from sqlalchemy import func
from sqlalchemy.ext.hybrid import hybrid_property

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
    _employee_id = Column("employee_id", db.String(16), unique=True, nullable=True)

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

        employee_id = kwargs.pop("employee_id", None)

        db.Model.__init__(
            self,
            username=username,
            company_email=company_email,
            personal_email=personal_email,
            _employee_id=employee_id,
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

    @hybrid_property
    def employee_id(self) -> Optional["EmployeeID"]:
        if self._employee_id is None:
            return None
        return EmployeeID(self._employee_id)

    @employee_id.setter
    def employee_id(self, val: Union[str, int, "EmployeeID", None]) -> None:

        if not (val is None or isinstance(val, EmployeeID)):
            val = EmployeeID(val).to_str()

        self._employee_id = val

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


"""
Employee ID abstracts the standardization of employee_id's project wide

* Comparisons to other employee ids
* Handle numeric and string inputs
* Comparisons to strings and integers
"""


class EmployeeID:
    """Standardize behavior and comparison of employee IDs"""

    LENGTH = 5
    FRONT_PAD_CHAR = "0"
    PREFIX = None
    CASE = "upper"

    def __init__(self, id: Union[str, int]):
        self._id = str(id)

    def __eq__(self, other: Any) -> bool:
        if other is None:
            raise TypeError("other can not be NoneType")
        if not isinstance(other, EmployeeID):
            other_str = EmployeeID(other).to_str()
        else:
            other_str = other.to_str()

        return self.to_str() == other_str

    def __hash__(self):
        return hash(self.to_str())

    def __str__(self) -> str:
        return self.to_str()

    def __repr__(self):
        return f"{type(self).__name__}({repr(self._id)})"

    def _pad_id(self, _id: str) -> str:
        """Add padding to the front of ID until desired length"""
        out = _id

        if self.PREFIX:
            out = self.PREFIX + out

        if self.LENGTH and len(out) < self.LENGTH:
            n_pad = self.LENGTH - len(out)
            assert n_pad >= 1

            pad_str = self.FRONT_PAD_CHAR * n_pad
            out = pad_str + out

        # remove padded characters from front of string
        if self.LENGTH and len(out) > self.LENGTH:
            n_pad_to_remove = len(out) - self.LENGTH
            if out[:n_pad_to_remove] == self.FRONT_PAD_CHAR * n_pad_to_remove:
                out = out[n_pad_to_remove:]

        return out

    def _pre_format(self, _id: str) -> str:
        """
        Adjust the character content of the string, i.e. handle padding or strip
        whitespace.
        """
        out = _id
        out = out.strip()
        out = self._pad_id(out)

        return out

    def _format(self, _id: str) -> str:
        out = _id

        return out

    def _post_format(self, _id: str) -> str:
        """Add final formatting to ID"""
        out = _id

        out = self._apply_case(out)
        return out

    def _apply_case(self, _id: str) -> str:
        """Apply case setting to id string"""
        out = _id

        cases = {
            "upper": str.upper,
            "lower": str.lower,
        }
        case_callable = cases.get(self.CASE)

        if case_callable:
            out = case_callable(out)

        return out

    def to_str(self) -> str:
        """Return the final formatted ID"""
        out = str(self._id)

        out = self._pre_format(out)
        out = self._format(out)
        out = self._post_format(out)

        return out
