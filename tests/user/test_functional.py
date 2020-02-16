from unittest import mock
import pytest

from flask import url_for
from webtest import TestResponse

from seniority_visualizer_app.shared import ResponseFailure


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
    "patch_send_company_confirmation_email_request"
)
class TestUserRequestsAccess:
    def test_user_submits_valid_email(self, testapp, clean_db, patch_send_company_confirmation_email_usecase):
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
        res.mustcontain(
            f"Email sent to {email}", no=[
                "Email not sent"
            ]
        )

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

        res.mustcontain(
            "Company Email - Invalid company email", no=[
                "Email sent to"
            ]
        )

    def test_system_error_occurs(self, testapp, clean_db, patch_send_company_confirmation_email_usecase):
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