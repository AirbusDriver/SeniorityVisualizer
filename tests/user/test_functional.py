from unittest import mock
import pytest

from flask import url_for
from webtest import TestResponse

from seniority_visualizer_app.shared import ResponseFailure
from seniority_visualizer_app.user.models import User


# todo: will be moved to user blueprint
@pytest.fixture
def patch_send_company_confirmation_email_usecase():
    """Mock an initialized SendConfirmationEmailUseCase"""
    with mock.patch(
        "seniority_visualizer_app.public.views.SendConfirmationEmailUseCase"
    ) as mock_usecase:
        yield mock_usecase


@pytest.fixture
def patch_send_company_confirmation_email_request():
    """Mock an initialized SendConfirmationEmailUseCase"""
    with mock.patch(
        "seniority_visualizer_app.public.views.SendCompanyConfirmationEmailRequest"
    ) as mock_request:
        yield mock_request


@pytest.mark.usefixtures(
    "patch_send_company_confirmation_email_usecase",
    "patch_send_company_confirmation_email_request",
)
class TestUserRequestsAccess:
    def test_user_submits_valid_email(
        self, testapp, clean_db, patch_send_company_confirmation_email_usecase
    ):
        """
        Given a user that has an email that is not already registered
        And the new user inputs a valid email into the request verification form
        When the user clicks the submit button
        Then the user should see that an email was sent
        And the user should see instructions on how soon the request will timeout
        """
        use_case = patch_send_company_confirmation_email_usecase()

        exec_return = mock.MagicMock()
        exec_return.__bool__.return_value = True

        use_case.execute.return_value = exec_return

        # BEGIN

        email = "some.user@jetblue.com"

        res: TestResponse = testapp.get(url_for("public.request_company_verification"))

        res.form["company_email"] = email

        res = res.form.submit().follow()

        assert res.status_code == 200
        res.mustcontain(f"Email sent to {email}", no=["Email not sent"])

    def test_user_submits_invalid_email(self, testapp, clean_db):
        """
        Given a user that is not already in the database
        And the user enters an invalid company email
        When the user submits the form
        Then the user is shown an error
        And the user is shown the form again
        """
        email = "some.user@bad.com"

        res: TestResponse = testapp.get(url_for("public.request_company_verification"))

        res.form["company_email"] = email

        res = res.form.submit().maybe_follow()

        res.mustcontain("Company Email - Invalid company email", no=["Email sent to"])

    def test_system_error_occurs(
        self, testapp, clean_db, patch_send_company_confirmation_email_usecase
    ):
        """
        Given a user that is not already in the database
        And the user enters a valid company email
        When the user submits the form
        And a system error occurs
        Then the user is shown the system error has occurred
        """
        use_case = patch_send_company_confirmation_email_usecase()
        response = ResponseFailure.build_system_error("Some message")
        use_case.execute.return_value = response

        email = "some.user@jetblue.com"

        res: TestResponse = testapp.get(url_for("public.request_company_verification"))

        res.form["company_email"] = email

        res = res.form.submit().maybe_follow()

        res.mustcontain("Email not sent, an internal error occurred!")


@pytest.mark.usefixtures("app", "clean_db")
class TestUserClicksConfirmationEmail:
    def test_user_clicks_valid_link(self, testapp):
        """
        Given an anonymous user has been sent an email with a valid confirmation token
        When the user clicks the token before the token expires
        Then the user should see a registration page
        And the user should not see errors
        """
        from seniority_visualizer_app.public.views import (
            get_current_flask_app_email_tokenizer,
        )

        user_email = "test.employee@jetblue.com"
        tokenizer = get_current_flask_app_email_tokenizer()

        verification_token = tokenizer.create_email_token(user_email)
        link = url_for(
            "public.verify_access_token", token=verification_token, _external=True
        )

        res: TestResponse = testapp.get(link)

        assert res.status_int == 302

        res = res.follow()

        res.mustcontain(f"Registration for {user_email}")

    def test_user_clicks_invalid_link(self, testapp):
        """
        Given an anonymous user
        When the user clicks an invalid link
        Then the user should see an error
        And the user should be redirected to home page
        """
        from seniority_visualizer_app.public.views import (
            get_current_flask_app_email_tokenizer,
        )

        user_email = "test.employee@jetblue.com"
        tokenizer = get_current_flask_app_email_tokenizer()

        verification_token = tokenizer.create_email_token(user_email) + "bad"
        link = url_for(
            "public.verify_access_token", token=verification_token, _external=True
        )

        res: TestResponse = testapp.get(link).follow()

        res.mustcontain(
            "This is an invalid link. Please request a new one or contact the admin.",
            no=[f"Registration for {user_email}"],
        )


@pytest.mark.usefixtures("app", "clean_db")
class TestUserSubmitsVerifiedRegistration:
    EMAIL = "test.employee@jetblue.com"

    def make_link(self):
        """Return a link with a good company email payload"""
        from seniority_visualizer_app.public.views import (
            get_current_flask_app_email_tokenizer,
        )

        user_email = "test.employee@jetblue.com"
        tokenizer = get_current_flask_app_email_tokenizer()

        verification_token = tokenizer.create_email_token(user_email)
        link = url_for(
            "public.verify_access_token", token=verification_token, _external=True
        )

        return link

    def test_new_user_registers(self, testapp):
        """
        Given a user has received a valid token
        When the user submits the form information successfully
        Then the user should be added
        And the user should be confirmed
        """
        res: TestResponse = testapp.get(self.make_link()).follow()

        form = res.forms["verified-registration-form"]

        form["username"] = "new_user"
        form["password"] = "123123"
        form["confirm_password"] = "123123"

        res = form.submit().follow()

        user = User.query.filter(User.username == "new_user").first()

        res.mustcontain("Welcome new_user!")

        retrieved = User.query.filter(User.username == user.username).first()
        assert retrieved is not None
        assert retrieved.company_email_confirmed
        assert retrieved.role.name == "ConfirmedUser"
        assert retrieved.personal_email is None
        assert retrieved.use_personal_email is False

    def test_new_user_registers_with_personal_email(self, testapp):
        res: TestResponse = testapp.get(self.make_link()).follow()

        form = res.forms["verified-registration-form"]

        form["username"] = "new_user"
        form["password"] = "123123"
        form["confirm_password"] = "123123"
        form["personal_email"] = "personal_email@example.com"
        form.set("use_personal_email", "y")

        res = form.submit().follow()

        user = User.query.filter(User.username == "new_user").first()

        res.mustcontain("Welcome new_user!")

        retrieved = User.query.filter(User.username == user.username).first()
        assert retrieved is not None
        assert retrieved.company_email_confirmed
        assert retrieved.role.name == "ConfirmedUser"
        assert retrieved.personal_email == "personal_email@example.com"
        assert retrieved.use_personal_email is True
