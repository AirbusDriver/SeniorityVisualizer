import pytest
from bs4 import BeautifulSoup
from flask import url_for

from seniority_visualizer_app.app import mail
from seniority_visualizer_app.user.models import User
from tests.factories import UserFactory


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

    def test_user_can_edit_own_details_but_not_others(self, testapp, logged_in_user):
        other_user = UserFactory()
        other_user.save()

        res = testapp.get(url_for("user.details", user_id=logged_in_user.id))

        res.mustcontain(logged_in_user.personal_email)
        res.mustcontain(logged_in_user.company_email)

        res = testapp.get(
            url_for("user.details", user_id=other_user.id), expect_errors=True
        )

        assert res.status_code == 401

    def test_user_can_add_employee_number_in_user_details(self, testapp, logged_in_user):
        logged_in_user.update(employee_id=None)
        assert logged_in_user.employee_id is None

        res = testapp.get(url_for("user.details", user_id=logged_in_user.id))

        form = res.forms["userDetailsForm"]

        assert form["employee_number"].value == ""

        form["employee_number"] = "123"

        res = form.submit().maybe_follow()

        form = res.forms["userDetailsForm"]

        assert form["employee_number"].value == "123"
        assert str(logged_in_user.employee_id) == "00123"
