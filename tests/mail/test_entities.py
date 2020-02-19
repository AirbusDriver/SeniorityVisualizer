import pytest
from unittest import mock

from itsdangerous.exc import BadTimeSignature

from seniority_visualizer_app.mail.entities import (
    MailClientResponse,
    Mailer,
    IMailService,
    MultiDict,
    EmailTokenizer,
    EmailTokenVerificationReason,
    EmailTokenVerificationResponse,
)


@pytest.fixture
def mocked_mailer():
    service = mock.MagicMock(autospec=IMailService)

    return Mailer(service=service())


@pytest.fixture
def email_tokenizer():
    tokenizer = EmailTokenizer("some_key", timeout=(60 * 60))
    return tokenizer


def test_send_text_html_mail_success(mocked_mailer):
    mailer = mocked_mailer  # brevity alias
    mailer.service.send_mail.return_value = MailClientResponse.from_success(
        response={"message": "message sent", "status": 200,}
    )

    TO = "some bloke"
    SUBJECT = "Some message"
    FROM = "Registration <registration@Domain.com>"
    TEXT = "Some message body"
    HTML = f"<p>{TEXT}</p>"
    DATA = MultiDict({"o:testmode": "yes"})

    response = mailer.send_mail(
        to=TO, subject=SUBJECT, from_=FROM, text=TEXT, html=HTML, data=DATA
    )

    mocked_mailer.service.send_mail.assert_called_with(
        to=TO, subject=SUBJECT, from_=FROM, text=TEXT, html=HTML, data=DATA
    )

    assert response is mailer.service.send_mail.return_value


def test_send_text_html_mail_failure(mocked_mailer):
    mailer = mocked_mailer
    mailer.service.send_mail.side_effect = ValueError("missing param")

    response = mailer.send_mail(
        to="doesn't",
        subject="really",
        from_="matter",
        text="what",
        html="these",
        data=MultiDict({"values": "are"}),
    )

    assert not response
    assert response.message == "ValueError: missing param"


class TestTokenizer:
    EMAIL = "some@company.email"

    def test_fixture(self, email_tokenizer):
        assert email_tokenizer.serializer is not None

    def test_create_email_token(self, email_tokenizer):
        token = email_tokenizer.create_email_token(self.EMAIL)

        assert isinstance(token, str)

    def test_parse_email_token_success(self, email_tokenizer):
        token = email_tokenizer.create_email_token(self.EMAIL)

        res = email_tokenizer.parse_email_token(token)

        assert res.successful
        assert res.payload == self.EMAIL

    def test_parse_email_token_bad_token(self, email_tokenizer):
        token = email_tokenizer.create_email_token(self.EMAIL) + "additional"

        res = email_tokenizer.parse_email_token(token)

        assert res.successful is False
        assert res.reason == email_tokenizer.reasons.BAD_TOKEN
        assert "Signature" in res.message

    def test_parse_email_token_timeout(self, email_tokenizer):
        mock_serializer = mock.MagicMock()
        mock_serializer.loads.side_effect = BadTimeSignature("Bad time")

        email_tokenizer.set_serializer(mock_serializer)

        token = email_tokenizer.create_email_token(self.EMAIL)

        res = email_tokenizer.parse_email_token(token)

        assert res.successful is False
        assert res.message == "Bad time"
        assert res.reason == email_tokenizer.reasons.TIMEOUT

    def test_verify_email_token(self, email_tokenizer):
        token = email_tokenizer.create_email_token(self.EMAIL)

        res = email_tokenizer.verify_email_token(
            token, self.EMAIL, case_insensitive=False
        )

        assert res == EmailTokenVerificationResponse(
            successful=True,
            reason=email_tokenizer.reasons.SUCCESS,
            message="SUCCESS",
            payload=self.EMAIL,
        )

    def test_verify_email_token_case_sensitive(self, email_tokenizer):
        token = email_tokenizer.create_email_token(self.EMAIL.upper())

        res = email_tokenizer.verify_email_token(
            token, self.EMAIL, case_insensitive=True
        )

        assert res == EmailTokenVerificationResponse(
            successful=True,
            reason=EmailTokenVerificationReason.SUCCESS,
            message="SUCCESS",
            payload=self.EMAIL,
        )

    def test_verify_email_token_timeout(self, email_tokenizer):
        from itsdangerous.exc import BadTimeSignature

        email_tokenizer.serializer.loads = mock.MagicMock(
            side_effect=BadTimeSignature("bad")
        )

        res = email_tokenizer.verify_email_token("test", "test")

        assert res.successful is False
        assert res.reason == EmailTokenVerificationReason.TIMEOUT

    def test_verify_email_token_bad_payload(self, email_tokenizer):
        from itsdangerous.exc import BadSignature

        email_tokenizer.serializer.loads = mock.MagicMock(
            side_effect=BadSignature("bad")
        )

        res = email_tokenizer.verify_email_token("test", "other")

        assert res.successful is False
        assert res.reason == EmailTokenVerificationReason.BAD_TOKEN
        assert "bad" in res.message

    def test_end_to_end(self, email_tokenizer):
        token = email_tokenizer.create_email_token(self.EMAIL)

        res = email_tokenizer.verify_email_token(token, self.EMAIL)

        assert res.successful is True
