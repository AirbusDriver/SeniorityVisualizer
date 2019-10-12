# -*- coding: utf-8 -*-
"""User views."""
from flask import (
    Blueprint,
    request,
    render_template,
    current_app,
    redirect,
    url_for,
    flash,
)
from flask_login import login_required, current_user
from itsdangerous.exc import SignatureExpired
from sqlalchemy.exc import IntegrityError
from pprint import pformat

blueprint = Blueprint("user", __name__, url_prefix="/users", static_folder="../static")

from .models import User
from .email import compare_emails
from .forms import UserDetailsForm, ChangePasswordForm
from seniority_visualizer_app.utils import flash_errors


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
        current_app.logger.info("EXPIRED TOKEN EVENT")
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
        current_app.logger.error("error occurred confirming user", exc_info=True)
        flash("Error occured. Please sign in to resend token!")
    else:
        flash("Thank you for confirming you email!")
        return redirect(url_for("public.home"))

    return render_template("users/confirmation_failure.html")


@blueprint.route("/details/<int:user_id>", methods=["GET", "POST"])
@login_required
def details(user_id):
    user: User = User.get_by_id(user_id)

    if not user or (current_user.id != user_id and not current_user.is_admin):
        return render_template("401.html")

    form = UserDetailsForm(
        user=user,
        username=user.username,
        company_email=user.company_email,
        personal_email=user.personal_email,
    )

    current_app.logger.debug(pformat(vars(user)))

    if form.validate_on_submit():
        try:
            user.username = form.username.data.strip()
            user.company_email = form.company_email.data.strip()
            user.personal_email = form.personal_email.data.strip()
            user.update(commit=True)
        except IntegrityError:
            current_app.logger.exception(f"IN -> user.views.details...\n" f"{user}")
            flash("INTEGRITY ERROR!! Error logged.")
            return redirect(url_for(".details", user_id=user.id))
        else:
            flash(
                "Successfully changed.. if you changed either email, you must confirm it",
                "success",
            )

    flash_errors(form)
    return render_template("users/detail.html", form=form)


@blueprint.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    """Change current user password"""

    user: User = current_user

    form = ChangePasswordForm()

    if form.validate_on_submit():
        if user.check_password(form.old_password.data):
            new_password = form.new_password.data

            assert (
                form.confirm_new_password.data == new_password
            ), "somehow the change password fields do not match"

            user.set_password(new_password)
            user.save(commit=True)
            flash(
                "Your password has been changed. You may log back in with your new password now.",
                "success"
            )
            current_app.logger.info(
                f"{current_user} changed password"
            )
        else:
            flash("Incorrect password!", "warning")

    flash_errors(form)
    return render_template("users/change_password.html", form=form)
