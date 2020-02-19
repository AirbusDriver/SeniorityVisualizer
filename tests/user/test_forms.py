from unittest import mock

import pytest

from seniority_visualizer_app.user import forms


class TestEmployeeValidationForm:

    @pytest.mark.parametrize("email", [
        "test.user@jetblue.com",
        "tu12345@jetblue.com",
        "TEST.USER@JETBLUE.COM",
        "TU12452@JeTblue.com"
    ])
    def test_valid_emails(self, email, app):
        with mock.patch("seniority_visualizer_app.user.forms.User") as mock_user:
            mock_user.get_by_email.return_value = None

            form = forms.EmployeeValidationForm(
                company_email=email
            )

            form.validate()

            assert form.errors == {}

    @pytest.mark.parametrize("email", [
        "test.user@jetblue.com",
        "tu12345@jetblue.com",
        "TEST.USER@JETBLUE.COM",
        "TU12452@JeTblue.com"
    ])
    def test_valid_email_already_exists(self, email, app):
        with mock.patch("seniority_visualizer_app.user.forms.User") as mock_user:
            mock_user.get_by_email.return_value = mock.MagicMock()

            form = forms.EmployeeValidationForm(
                company_email=email
            )

            form.validate()

            assert form.errors == {
                "company_email": ["Email already registered"]
            }


    @pytest.mark.parametrize("email", [
        "test",
        "test@unitedairlines.com"
    ])
    def test_invalid_emails(self, email, app):
        with mock.patch("seniority_visualizer_app.user.forms.User") as mock_user:
            mock_user.get_by_email.return_value = None

            form = forms.EmployeeValidationForm(
                company_email=email
            )

            form.validate()

            assert form.errors == {
                "company_email": ["Invalid company email"]
            }
