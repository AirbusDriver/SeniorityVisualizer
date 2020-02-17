"""
Decorators module.

Route decorators
"""
from functools import wraps

from flask import abort
from flask_login import current_user

from seniority_visualizer_app.user.role import Permissions


def permissions_required(*permissions: Permissions):
    """Require logged in user to have all permissions passed (or is admin) else abort(401)"""

    def decorator(func):
        @wraps(func)
        def _view(*args, **kwargs):
            total_perms = sum(permissions)
            user_has_perms = current_user.role.has_permission(total_perms)
            if not (
                user_has_perms or current_user.role.has_permission(Permissions.ADMIN)
            ):
                abort(401)
            return func(*args, **kwargs)

        return _view

    return decorator


def admin_required(func):
    """Require admin permission on view"""
    return permissions_required(Permissions.ADMIN)(func)
