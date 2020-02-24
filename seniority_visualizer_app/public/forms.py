# -*- coding: utf-8 -*-
"""Public forms."""
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, BooleanField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Email, ValidationError

from seniority_visualizer_app.user.models import User, Permissions


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        """Create instance."""
        super(LoginForm, self).__init__(*args, **kwargs)
        self.user = None

    def validate(self):
        """Validate the form."""
        initial_validation = super(LoginForm, self).validate()
        if not initial_validation:
            return False

        self.user = User.query.filter(User.username.ilike(self.username.data)).first()
        if not self.user:
            self.username.errors.append("Unknown username")
            return False

        if not self.user.check_password(self.password.data):
            self.password.errors.append("Invalid password")
            return False

        if not self.user.active and not self.user.role.has_permission(
            Permissions.ADMIN
        ):
            self.username.errors.append("User not activated")
            return False
        return True


class PostVerificationRegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField(
        "Confirm Password", [EqualTo("password"), DataRequired()]
    )
    personal_email = StringField(
        "Personal Email", description="Can be used for things like password resets"
    )
    use_personal_email = BooleanField("Use Personal Email")
    submit = SubmitField()

    def validate_personal_email(self, field):
        personal_email = self.personal_email.data

        if self.use_personal_email.data:
            Email()(self, field)
            user = User.get_by_email(
                User.personal_email, personal_email, case_insensitive=True
            )
            if user:
                field.errors.append(
                    f"{personal_email} already registered! Message admin if you believe this to be an error."
                )

    def validate_username(self, field):
        username = field.data
        if User.query.filter(User.username.ilike(username)).first():
            raise ValidationError(
                f"{username} already registered. Pick a new username."
            )
