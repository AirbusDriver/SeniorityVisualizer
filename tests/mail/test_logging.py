import pytest
from unittest import mock
import logging

from seniority_visualizer_app.mail.entities import Mailer


def assert_string_in_messages(s, messages):
    assert any(s in _ for _ in messages), f"{s} not in {messages}"


class TestMailerLogging:
    def test_send_mail_successful(self, app, caplog):
        caplog.set_level(logging.DEBUG)

        mock_service = mock.MagicMock()
        mailer = Mailer(mock_service)

        mailer.send_mail(
            to="this",
            subject="really",
            from_="doesnt",
            text="matter",
            data={"all": "that much"},
        )

        assert_string_in_messages("Trying Mailer.send_mail()", caplog.messages)
        assert_string_in_messages(
            "Sending mail using 'MagicMock' service", caplog.messages
        )

    def test_send_mail_logs_exception(self, app, caplog):
        caplog.set_level(logging.DEBUG)

        mock_service = mock.MagicMock()
        mock_service.send_mail.side_effect = RuntimeError("Some error")

        mailer = Mailer(mock_service)

        mailer.send_mail(
            to="this",
            subject="really",
            from_="doesnt",
            text="matter",
            data={"all": "that much"},
        )

        assert_string_in_messages("RuntimeError: Some error", caplog.text.split("\n"))
        assert_string_in_messages(
            "Error occurred in mail client using MagicMock.send_mail()", caplog.messages
        )
