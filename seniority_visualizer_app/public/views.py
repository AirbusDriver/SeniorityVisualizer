# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""
from pprint import pprint, pformat
from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import login_required, login_user, logout_user

from seniority_visualizer_app.extensions import login_manager
from seniority_visualizer_app.public.forms import LoginForm
from seniority_visualizer_app.user.email import send_confirmation_email
from seniority_visualizer_app.user.forms import RegisterForm, EmployeeValidationForm
from seniority_visualizer_app.user.models import User
from seniority_visualizer_app.utils import flash_errors
from seniority_visualizer_app.shared.global_entities import get_current_flask_app_email_tokenizer, \
    get_current_flask_app_mailer
from seniority_visualizer_app.mail.use_cases.usecase_requests import SendCompanyConfirmationEmailRequest
from seniority_visualizer_app.mail.use_cases.interactors import SendConfirmationEmailUseCase

blueprint = Blueprint("public", __name__, static_folder="../static")


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID."""
    return User.get_by_id(int(user_id))


@blueprint.route("/", methods=["GET", "POST"])
def home():
    """Home page."""
    form = LoginForm(request.form)
    # Handle logging in
    if request.method == "POST":
        if form.validate_on_submit():
            login_user(form.user)
            flash("You are logged in.", "success")
            redirect_url = request.args.get("next") or url_for(".home")
            return redirect(redirect_url)
        else:
            flash_errors(form)
    return render_template("public/home.html", form=form)


@blueprint.route("/logout/")
@login_required
def logout():
    """Logout."""
    logout_user()
    flash("You are logged out.", "info")
    return redirect(url_for("public.home"))


@blueprint.route("/register/", methods=["GET", "POST"])
def register():
    """Register new user."""
    logger = current_app.logger

    form = RegisterForm(request.form)
    if form.validate_on_submit():
        user = User.create(
            username=form.username.data,
            company_email=form.company_email.data,
            personal_email=form.personal_email.data,
            password=form.password.data,
            active=True,
            employee_id=form.employee_number.data,
        )

        logger.info(f"NEW USER -> {form.username.data}")

        send_confirmation_email(user, User.email_categories.PERSONAL_EMAIL)
        send_confirmation_email(user, User.email_categories.COMPANY_EMAIL)

        flash("Thank you for registering. You can now log in.", "success")
        flash("You must confirm both emails within the next hour!")
        return redirect(url_for("public.home"))
    else:
        flash_errors(form)
    return render_template("public/register.html", form=form)


# todo: move to user blueprint
@blueprint.route("/request_access/", methods=["GET", "POST"])
def request_company_verification():
    """User can request access with company ID here"""
    logger = current_app.logger

    form = EmployeeValidationForm()

    if form.validate_on_submit():
        current_app.logger.debug(f"{type(form).__name__} Form validated")

        serializer = get_current_flask_app_email_tokenizer()

        email = form.company_email.data.lower().strip()
        token = serializer.create_email_token(email)

        current_app.logger.debug(f"Token created for {email} -> {token}")

        req = SendCompanyConfirmationEmailRequest.from_dict({
            "company_email": email,
            "verification_link": url_for(".verify_access_token", token=token, _external=True)
        })

        logger.debug(f"USE CASE REQUEST: {type(req).__name__} -> \n{pformat(vars(req))}")

        mailer = get_current_flask_app_mailer()

        res = SendConfirmationEmailUseCase(
            mailer=mailer
        ).execute(req)

        if res:
            flash(f"Email sent to {email}")
        elif not res and res.type == res.SYSTEM_ERROR:
            flash("Email not sent, an internal error occurred!")

        return redirect(url_for(".request_company_verification"))

    if request.method == "POST":
        flash_errors(form)

    return render_template("public/company_verification.html", validation_form=form)


@blueprint.route("/verify_access/<token>")
def verify_access_token(token):
    return "verify access"


@blueprint.route("/about/")
def about():
    """About page."""
    form = LoginForm(request.form)
    return render_template("public/about.html", form=form)
