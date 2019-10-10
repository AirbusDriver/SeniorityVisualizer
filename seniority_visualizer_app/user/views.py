# -*- coding: utf-8 -*-
"""User views."""
from flask import Blueprint, render_template, current_app, redirect, url_for, flash
from flask_login import login_required
from itsdangerous.exc import SignatureExpired

blueprint = Blueprint("user", __name__, url_prefix="/users", static_folder="../static")

from .models import User
from .email import compare_emails


@blueprint.route("/")
@login_required
def members():
    """List members."""
    return render_template("users/members.html")


@blueprint.route("/confirm_user/<token>")
def confirm_user(token):
    """Confirm email"""
    try:
        payload = User.parse_confirmation_token(token)
    except SignatureExpired:
        current_app.logger.info(
            "EXPIRED TOKEN EVENT"
        )
        flash("Confirmation link expired!")
        return render_template("users/confirmation_failure.html", expired=True)

    user_id = int(payload["user_id"])
    category = payload["email_category"]
    email = payload["email"].lower().strip()

    try:
        user = User.get_by_id(user_id)
        existing_email = getattr(user, category)
        if user and compare_emails(email, existing_email):
            user.confirm_email(category)
        else:
            current_app.logger.info(
                f"EMAIL CONFIRMATION FAIL\n"
                f"{user} attempted confirmation of {category} email type \n"
                f"EXISTING: {existing_email} CONFIRMING: {email}"
            )
            return render_template("users/confirmation_failure.html")
    except Exception as exc:
        current_app.logger.error('error occurred confirming user', exc_info=True)
        flash("Error occured. Please sign in to resend token!")
    else:
        flash("Thank you for confirming you email!")
        return redirect(url_for("public.home"))

    return render_template("users/confirmation_failure.html")
