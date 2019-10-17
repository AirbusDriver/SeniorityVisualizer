from enum import auto, unique
from sqlalchemy import Boolean, Integer
from typing import Union, Dict

from seniority_visualizer_app.database import SurrogatePK, Model, Column
from seniority_visualizer_app.extensions import db
from seniority_visualizer_app.user.utils import BaseTwoAutoEnum


@unique
class Permissions(BaseTwoAutoEnum):
    """Enumeration of the permission types"""
    ADMIN = auto()
    VIEW_SENIORITY_DATA = auto()
    EDIT_SENIORITY_DATA = auto()
    VIEW_USER_DETAILS = auto()
    EDIT_USER_DETAILS = auto()
    VIEW_USERS = auto()


def generate_permission_sets() -> Dict[str, set]:
    """
    Return a dict containing the role names and the permissions each has
    """
    p = Permissions  # alias for brevity

    unconfirmed_user = {
        p.VIEW_USER_DETAILS, p.EDIT_USER_DETAILS
    }

    confirmed_user = {
        p.VIEW_SENIORITY_DATA, p.VIEW_USERS
    }.union(unconfirmed_user)

    admin_user = {
        p.EDIT_SENIORITY_DATA, p.ADMIN
    }.union(confirmed_user)

    roles = {
        "UnconfirmedUser": unconfirmed_user,
        "ConfirmedUser": confirmed_user,
        "Admin": admin_user,
    }

    return roles


class Role(SurrogatePK, Model):
    """A role for a user."""

    __tablename__ = "roles"
    name = Column(db.String(80), unique=True, nullable=False)
    default = Column(Boolean, default=False, index=True)
    permissions = Column(Integer)

    def __init__(self, name, **kwargs):
        """Create instance."""
        db.Model.__init__(self, name=name, **kwargs)
        if self.permissions is None:
            self.permissions = 0

    def __repr__(self):
        """Represent instance as a unique string."""
        return "<Role({name})>".format(name=self.name)

    def add_permission(self, perm: Union[Permissions, int]):
        """Add permission to role."""
        if isinstance(perm, Permissions):
            perm = perm.value
        self.permissions += perm

    def remove_premission(self, perm: Union[Permissions, int]):
        """Remove a permission from a role."""
        if isinstance(perm, Permissions):
            perm = int(perm)
        self.permissions -= perm

    def has_permission(self, perm: Union[Permissions, int]) -> bool:
        """Return True is a role has a permission."""
        if isinstance(perm, Permissions):
            perm = perm.value
        return self.permissions & perm == perm

    def reset_permissions(self):
        """Reset all permissions on role."""
        self.permissions = 0

    @staticmethod
    def _create_roles():
        """
        Return roles with populated permissions.

        :return:
        """

        roles = generate_permission_sets()

        out = {}

        for role_name, perm_set in roles.items():
            role = Role.query.filter(Role.name.ilike(role_name)).first() or Role(role_name)
            role.reset_permissions()
            role.add_permission(
                sum(perm.value for perm in perm_set)
            )
            out[role_name] = role

        return out

    @staticmethod
    def insert_roles():
        """Populate the database with roles"""
        roles = Role._create_roles()
        default = "UnconfirmedUser"

        for role_name, role in roles.items():
            if role.name == default:
                role.default = True
            role.save()
