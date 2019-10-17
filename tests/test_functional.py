# -*- coding: utf-8 -*-
"""Functional tests using WebTest.

See: http://webtest.readthedocs.org/
"""
from unittest import mock

from flask import url_for

from seniority_visualizer_app.user.models import User
from .factories import UserFactory


class TestLoggingIn:
    """Login."""

    def test_can_log_in_returns_200(self, user, testapp):
        """Login successful."""
        # Goes to homepage
        res = testapp.get("/")
        # Fills out login form in navbar
        form = res.forms["loginForm"]
        form["username"] = user.username
        form["password"] = "myprecious"
        # Submits
        res = form.submit().follow()
        assert res.status_code == 200

    def test_sees_alert_on_log_out(self, user, testapp):
        """Show alert on logout."""
        res = testapp.get("/")
        # Fills out login form in navbar
        form = res.forms["loginForm"]
        form["username"] = user.username
        form["password"] = "myprecious"
        # Submits
        res = form.submit().follow()
        res = testapp.get(url_for("public.logout")).follow()
        # sees alert
        assert "You are logged out." in res

    def test_sees_error_message_if_password_is_incorrect(self, user, testapp):
        """Show error if password is incorrect."""
        # Goes to homepage
        res = testapp.get("/")
        # Fills out login form, password incorrect
        form = res.forms["loginForm"]
        form["username"] = user.username
        form["password"] = "wrong"
        # Submits
        res = form.submit()
        # sees error
        assert "Invalid password" in res

    def test_sees_error_message_if_username_doesnt_exist(self, user, testapp):
        """Show error if username doesn't exist."""
        # Goes to homepage
        res = testapp.get("/")
        # Fills out login form, password incorrect
        form = res.forms["loginForm"]
        form["username"] = "unknown"
        form["password"] = "myprecious"
        # Submits
        res = form.submit()
        # sees error
        assert "Unknown user" in res


class TestRegistering:
    """Register a user."""

    @mock.patch("seniority_visualizer_app.public.views.send_confirmation_email")
    def test_can_register(self, mocked_send_conf_email, user, testapp):
        """Register a new user."""
        old_count = len(User.query.all())
        # Goes to homepage
        res = testapp.get("/")
        # Clicks Create Account button
        res = res.click("Create account")
        # Fills out the form
        form = res.forms["registerForm"]
        form["username"] = "foobar"
        form["personal_email"] = "foo@bar.com"
        form["company_email"] = "person@jetblue.com"
        form["password"] = "secret"
        form["confirm"] = "secret"
        # Submits
        res = form.submit().follow()
        assert mocked_send_conf_email.call_count == 2
        assert res.status_code == 200
        # A new user was created
        assert len(User.query.all()) == old_count + 1

    def test_sees_error_message_if_passwords_dont_match(self, user, testapp):
        """Show error if passwords don't match."""
        # Goes to registration page
        res = testapp.get(url_for("public.register"))
        # Fills out form, but passwords don't match
        form = res.forms["registerForm"]
        form["username"] = "foobar"
        form["personal_email"] = "foo@bar.com"
        form["company_email"] = "test@jetblue.com"
        form["password"] = "secret"
        form["confirm"] = "secrets"
        # Submits
        res = form.submit()
        # sees error message
        assert "Passwords must match" in res

    def test_sees_error_message_if_user_already_registered(self, user, testapp):
        """Show error if user already registered."""
        user = UserFactory(active=True)  # A registered user
        user.save()
        # Goes to registration page
        res = testapp.get(url_for("public.register"))
        # Fills out form, but username is already registered
        form = res.forms["registerForm"]
        form["username"] = user.username
        form["personal_email"] = "foo@bar.com"
        form["company_email"] = "test@jetblue.com"
        form["password"] = "secret"
        form["confirm"] = "secret"
        # Submits
        res = form.submit()
        # sees error
        assert "Username already registered" in res

    def test_sees_error_if_company_email_invalid(self, user, testapp):
        user = UserFactory(active=True)

        # Goes to registration page
        res = testapp.get(url_for("public.register"))
        # Fills out form with invalid company email
        form = res.forms["registerForm"]
        # Submits the form
        form["username"] = user.username
        form["company_email"] = "bademail@host.com"
        form["personal_email"] = "test@example.com"
        form["password"] = "12345"
        form["confirm"] = "12345"
        # Sees error about invalid company email
        res = form.submit()
        assert "Email is not a valid company email." in res


class TestRegistration:
    def test_user_created_with_emails_not_confirmed_and_then_confirmed(self, user: User, testapp):
        assert user
        assert user.company_email_confirmed == user.personal_email_confirmed == False

        # confirm personal email
        token = user.generate_confirmation_token(user.email_categories.PERSONAL_EMAIL)

        url = url_for("user.confirm_user", token=token)

        assert user.role.name == 'UnconfirmedUser'

        res = testapp.get(url).follow()

        assert res.status_int == 200
        assert user.personal_email_confirmed
        assert not user.company_email_confirmed

        res.mustcontain("Thank you for confirming you email!")

        assert user.role.name == 'UnconfirmedUser'

        # confirm company email

        token = user.generate_confirmation_token(user.email_categories.COMPANY_EMAIL)
        url = url_for("user.confirm_user", token=token)

        res = testapp.get(url).follow()

        res.mustcontain("Thank you for confirming you email!")

        assert user.role.name == "ConfirmedUser"

        assert res.status_code == 200
        assert user.personal_email_confirmed
        assert user.company_email_confirmed

    @mock.patch("seniority_visualizer_app.public.views.send_confirmation_email")
    def test_email_sent_alert_shown(self, mock_send, db, testapp):
        form = testapp.get(url_for("public.register")).forms["registerForm"]

        form["username"] = "TestUser"
        form["company_email"] = "test.user@jetblue.com"
        form["personal_email"] = "testUser@example.com"
        form["password"] = "password123"
        form["confirm"] = "password123"

        res = form.submit().follow()

        res.mustcontain("You must confirm both emails within the next hour!")

    @mock.patch("seniority_visualizer_app.public.views.send_confirmation_email")
    def test_email_sent_on_signup(self, patch_conf_email, db, testapp):
        form = testapp.get(url_for("public.register")).forms["registerForm"]

        form["username"] = "TestUser"
        form["company_email"] = "test.user@jetblue.com"
        form["personal_email"] = "testUser@example.com"
        form["password"] = "password123"
        form["confirm"] = "password123"

        res = form.submit().follow()

        assert patch_conf_email.call_count == 2
