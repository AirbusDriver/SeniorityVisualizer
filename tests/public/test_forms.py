from unittest import mock
import pytest

from seniority_visualizer_app.public.forms import PostVerificationRegistrationForm
from seniority_visualizer_app.user.models import User


@pytest.mark.usefixtures("clean_db")
class TestPostVerificationRegistrationForm:
    def test_submit_with_personal_email(self):
        form = PostVerificationRegistrationForm()

        form.username.data = "newuser"
        form.password.data = "test"
        form.confirm_password.data = "test"
        form.personal_email.data = "some.email@example.com"
        form.use_personal_email.data = True

        assert form.validate(), form.errors

    def test_submit_with_personal_email_no_check_box(self):
        form = PostVerificationRegistrationForm()

        form.username.data = "newuser"
        form.password.data = "test"
        form.confirm_password.data = "test"
        form.personal_email.data = "some.email@example.com"
        form.use_personal_email.data = ""

        assert form.validate(), form.errors

    @pytest.mark.parametrize("email", ["", "bademail"])
    def test_submit_with_checkbox_but_bad_email(self, email):
        form = PostVerificationRegistrationForm()

        form.username.data = "newuser"
        form.password.data = "test"
        form.confirm_password.data = "test"
        form.personal_email.data = email
        form.use_personal_email.data = True

        assert not form.validate()

        assert form.errors.get("personal_email") == [
            "Invalid email address."
        ], form.errors

    def test_submit_with_personal_email_but_user_registered(self, user):
        with mock.patch(
            "seniority_visualizer_app.public.forms.User.get_by_email"
        ) as mock_user_get:
            mock_user_get.return_value = user

        form = PostVerificationRegistrationForm()

        form.username.data = "newuser"
        form.password.data = "test"
        form.confirm_password.data = "test"
        form.personal_email.data = user.personal_email
        form.use_personal_email.data = True

        assert not form.validate()
        assert f"{user.personal_email} already registered!" in " ".join(
            form.personal_email.errors
        )

    def test_submit_with_username_taken(self, user):

        form = PostVerificationRegistrationForm()

        form.username.data = user.username
        form.password.data = "test"
        form.confirm_password.data = "test"
        form.personal_email.data = "somenewemail@example.com"
        form.use_personal_email.data = True

        assert not form.validate()
        assert f"{user.username} already registered." in " ".join(form.username.errors)
