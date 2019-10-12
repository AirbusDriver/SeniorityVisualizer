# -*- coding: utf-8 -*-
"""User forms."""
from flask import current_app
from flask_wtf import FlaskForm
from sqlalchemy import func
from wtforms import PasswordField, StringField, ValidationError
from wtforms.validators import DataRequired, Email, EqualTo, Length, InputRequired

from .models import User
from .validators import CompanyEmail


class RegisterForm(FlaskForm):
    """Register form."""

    username = StringField(
        "Username", validators=[DataRequired(), Length(min=3, max=25)]
    )
    company_email = StringField(
        "Company Email", validators=[DataRequired(), Email(), CompanyEmail()]
    )
    personal_email = StringField("Personal Email", validators=[DataRequired(), Email()])
    password = PasswordField(
        "Password", validators=[DataRequired(), Length(min=6, max=40)]
    )
    confirm = PasswordField(
        "Verify password",
        [DataRequired(), EqualTo("password", message="Passwords must match")],
    )

    def __init__(self, *args, **kwargs):
        """Create instance."""
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.user = None  # todo: remove?

    def validate(self):
        """Validate the form."""
        initial_validation = super(RegisterForm, self).validate()
        if not initial_validation:
            return False
        user = User.query.filter_by(username=self.username.data).first()
        if user:
            self.username.errors.append("Username already registered")
            return False
        if User.get_by_email(
            User.company_email, self.company_email.data, case_insensitive=True
        ):
            self.company_email.errors.append("Email already registered")
            return False
        if User.get_by_email(
            User.personal_email, self.personal_email.data, case_insensitive=True
        ):
            self.personal_email.errors.append("Email already registered")
            return False

        return True


class UserDetailsForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    company_email = StringField(
        "Company Email", validators=[DataRequired(), CompanyEmail(), Email()]
    )
    personal_email = StringField("Personal Email", validators=[DataRequired(), Email()])

    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def validate_username(self, field):
        current_app.logger.debug(f"FIELD: {field}\n" f"USER: {self.user.username}")
        lower_data = field.data.lower()

        if self.user.username.lower() != lower_data:
            current_app.logger.debug("CHANGE DETECTED")
            if User.query.filter(func.lower(User.username) == lower_data).first():
                raise ValidationError(f"{field.data} already registered!")

    # todo: refactor these validators
    def validate_company_email(self, field):
        lower_data = field.data.lower()

        current_app.logger.debug(f"FIELD: {field}\n" f"USER: {self.user.company_email}")

        if self.user.company_email.lower() != lower_data:
            current_app.logger.debug("CHANGE DETECTED")
            if User.query.filter(func.lower(User.company_email) == lower_data).first():
                raise ValidationError(f"{field.data} already registered!")

    def validate_personal_email(self, field):
        lower_data = field.data.lower()

        current_app.logger.debug(
            f"FIELD: {field}\n" f"USER: {self.user.personal_email}"
        )

        if self.user.personal_email.lower() != lower_data:
            current_app.logger.debug("CHANGE DETECTED")
            if User.query.filter(func.lower(User.personal_email) == lower_data).first():
                raise ValidationError(f"{field.data} already registered!")


class PasswordResetForm(FlaskForm):
    new_password = PasswordField(
        "New Password", validators=[InputRequired(), Length(6, 24)]
    )

    confirm_new_password = PasswordField(
        "Confirm New Password",
        validators=[
            InputRequired(),
            EqualTo("new_password", message="Passwords must match!"),
        ],
    )


class ChangePasswordForm(FlaskForm):
    personal_email = StringField(
        "Pesonal Email", validators=[InputRequired(), Email()]
    )
