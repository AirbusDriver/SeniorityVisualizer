# -*- coding: utf-8 -*-
"""User views."""
from flask import Blueprint, render_template, make_response
from flask_login import login_required

blueprint = Blueprint("user", __name__, url_prefix="/users", static_folder="../static")

from .models import User


@blueprint.route("/")
@login_required
def members():
    """List members."""
    return render_template("users/members.html")


@blueprint.route("/confirm_user/<token>")
def confirm_user(token):
    """Confirm email"""
    payload = User.parse_confirmation_token(token)

    if not payload:
        return make_response("not confirmed")

    try:
        user_id = int(payload["user_id"])
        category = payload["email_category"]
        email = payload["email"].lower().strip()

        user = User.get_by_id(user_id)

        if user and getattr(user, category).lower().strip() == email:
            user.confirm_email(category)
    except Exception as exc:
        print(exc)
    else:
        return make_response("confirmed")

    return make_response("not confirmed")
