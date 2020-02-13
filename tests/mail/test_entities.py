import pytest
from unittest import mock

from seniority_visualizer_app.mail.entities import MailClientResponse, Mailer, IMailService, MultiDict


@pytest.fixture
def mocked_mailer():
    service = mock.MagicMock(autospec=IMailService)

    return Mailer(service=service())


def test_send_text_html_mail_success(mocked_mailer):
    mailer = mocked_mailer  # brevity alias
    mailer.service.send_mail.return_value = MailClientResponse.from_success(
        response={
            "message": "message sent",
            "status": 200,
        }
    )

    TO = "some bloke"
    SUBJECT = "Some message"
    FROM = "Registration <registration@Domain.com>"
    TEXT = "Some message body"
    HTML = f"<p>{TEXT}</p>"
    DATA = MultiDict({"o:testmode": "yes"})

    response = mailer.send_mail(
        to=TO,
        subject=SUBJECT,
        from_=FROM,
        text=TEXT,
        html=HTML,
        data=DATA
    )

    mocked_mailer.service.send_mail.assert_called_with(
        to=TO,
        subject=SUBJECT,
        from_=FROM,
        text=TEXT,
        html=HTML,
        data=DATA
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
        data=MultiDict({"values": "are"})
    )

    assert not response
    assert response.message == "ValueError: missing param"
