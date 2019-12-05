# -*- coding: utf-8 -*-
"""Test forms."""
from unittest import mock

import pytest
from wtforms import ValidationError

from seniority_visualizer_app.public.forms import LoginForm
from seniority_visualizer_app.user.forms import RegisterForm
from seniority_visualizer_app.user.models import User
from seniority_visualizer_app.user.validators import CompanyEmail, UniqueField


class TestRegisterForm:
    """Register form."""

    def test_validate_user_already_registered(self, user):
        """Enter username that is already registered."""
        form = RegisterForm(
            username=user.username,
            personal_email="foo@bar.com",
            company_email="test@jetblue.com",
            password="example",
            confirm="example",
        )

        assert form.validate() is False
        assert "Username already registered" in form.username.errors

    def test_validate_email_already_registered(self, user):
        """Enter email that is already registered."""
        form = RegisterForm(
            username="unique",
            company_email="some_new_email@jetblue.com",
            personal_email=user.personal_email,
            password="example",
            confirm="example",
        )

        assert form.validate() is False
        assert "Email already registered" in form.personal_email.errors

    def test_validate_success(self, clean_db):
        """Register with success."""
        form = RegisterForm(
            username="newusername",
            personal_email="new@test.test",
            company_email="person@jetblue.com",
            password="example",
            confirm="example",
        )
        assert form.validate() is True


class TestLoginForm:
    """Login form."""

    def test_validate_success(self, user):
        """Login successful."""
        user.set_password("example")
        user.save()
        form = LoginForm(username=user.username, password="example")
        assert form.validate() is True
        assert form.user == user

    def test_validate_unknown_username(self, clean_db):
        """Unknown username."""
        form = LoginForm(username="unknown", password="example")
        assert form.validate() is False
        assert "Unknown username" in form.username.errors
        assert form.user is None

    def test_validate_invalid_password(self, user):
        """Invalid password."""
        user.set_password("example")
        user.save()
        form = LoginForm(username=user.username, password="wrongpassword")
        assert form.validate() is False
        assert "Invalid password" in form.password.errors

    def test_validate_inactive_user(self, user):
        """Inactive user."""
        user.active = False
        user.set_password("example")
        user.save()
        # Correct username and password, but user is not activated
        form = LoginForm(username=user.username, password="example")
        assert form.validate() is False
        assert "User not activated" in form.username.errors


class TestCompanyEmailValidator:
    @pytest.mark.parametrize(
        "email",
        [
            "thomas.edison@jetblue.com",
            "THOMAS.edison@jetblue.com",
            "TE12345@jetblue.com",
            "te12345@jetblue.com",
        ],
    )
    def test_is_valid_email_validates_correct_email(self, email):
        validator = CompanyEmail()

        assert validator.is_valid_email(email)

    @pytest.mark.parametrize(
        "email", ["wrong@host.com", "pretty_close@jetblue.con", "@jetblue.com", 4]
    )
    def test_is_valid_email_returns_false(self, email):
        validator = CompanyEmail()

        assert not validator.is_valid_email(email)


class TestUniqueValidator:
    def test_raises_user_field_that_exists(self, user):
        validator = UniqueField(User, "company_email")

        mock_form = mock.MagicMock()

        mock_field = mock.MagicMock()
        mock_field.data = user.company_email

        with pytest.raises(ValidationError) as exc_info:
            validator(mock_form, mock_field)

            assert "Already registered" in str(exc_info.value)

    def test_does_not_raise_when_not_registered(self, user):
        validator = UniqueField(User, "company_email")

        mock_form = mock.MagicMock()

        mock_field = mock.MagicMock()
        mock_field.data = "new email"

        assert validator(mock_form, mock_field)
