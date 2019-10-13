from unittest import mock

import pytest
from flask import url_for
from bs4 import BeautifulSoup

from seniority_visualizer_app.user.models import User
from seniority_visualizer_app.app import mail


def mock_make_msgid():
    return "<157093746497.29400.9452561162865134712@adder-ws>"


# todo: move to conftest
@pytest.fixture(scope="module")
def patch_mail_id():
    with mock.patch("flask_mail.make_msgid", side_effect=mock_make_msgid):
        yield


@pytest.fixture
def logged_in_user(testapp, user: User) -> User:
    """
    Return a user that is currently logged into the app.
    """
    res = testapp.get(url_for("public.home"))
    form = res.forms["loginForm"]
    form["username"] = user.username
    form["password"] = "myprecious"

    res = form.submit().maybe_follow()
    assert res.status_code == 200, "user unable to log in"

    yield user

    user.set_password("myprecious")
    user.save()
    assert user.check_password("myprecious"), "password not set to original password"


@pytest.mark.usefixtures("patch_mail_id")
class TestUserPasswordManagement:
    def test_user_can_change_password(self, testapp, logged_in_user):
        """
        Given a logged in User
        When a User submits a new password form
        Then the user is able to log in with the new password
        """
        res = testapp.get(url_for("user.change_password"))
        form = res.form

        new_pass = "newPassword!!"
        form["old_password"] = "myprecious"
        form["new_password"] = new_pass
        form["confirm_new_password"] = new_pass

        res = form.submit().maybe_follow()

        res.mustcontain("Your password has been changed.")

        res = testapp.get(url_for("public.logout"))

        assert logged_in_user.check_password(new_pass)

    def test_user_can_request_password_reset(self, testapp, user):
        """
        User can reset password via link and log back in after clicking link.

        Given an existing user
        When the user enters email in forgot password form
        Then an email is sent to the user containing password
        """
        res = testapp.get(url_for("user.forgot_password"))

        form = res.forms["forgotPasswordForm"]

        form["personal_email"] = user.personal_email

        with mail.record_messages() as outbox:
            res = form.submit().maybe_follow()

            assert len(outbox) == 1

            assert outbox[0].recipients == [user.personal_email]
            email_soup = BeautifulSoup(outbox[0].html, features="html.parser")

            reset_link = email_soup.select_one("#passwordResetLink")
            assert reset_link

        res = testapp.get(reset_link["href"])
        form = res.forms["passwordResetForm"]

        new_password = "new_password_123"

        form["new_password"] = new_password
        form["confirm_new_password"] = new_password

        res = form.submit().maybe_follow()

        res.mustcontain("You have successfully changed your password.")

        form = res.form

        form["username"] = user.username
        form["password"] = new_password

        res = form.submit().maybe_follow()

        res.mustcontain(url_for("public.logout"))
