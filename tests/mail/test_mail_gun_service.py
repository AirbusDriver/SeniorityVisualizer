import pytest
from unittest import mock

import requests
from werkzeug import MultiDict

from seniority_visualizer_app.mail.adapters import MailGunService
from ..settings import MAILGUN_API_KEY, MAILGUN_DOMAIN, MAILGUN_DEFAULT_SENDER

BASE_URL = f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}"


@pytest.fixture
def mail_gun():
    service = MailGunService(
        api_key=MAILGUN_API_KEY, domain=MAILGUN_DOMAIN, test_mode=True
    )
    service.client = mock.MagicMock(autospec=requests)
    return service


def test_fixture(mail_gun):
    assert mail_gun.domain == MAILGUN_DOMAIN
    assert mail_gun.api_key == MAILGUN_API_KEY
    assert mail_gun.test_mode is True


def test_base_url(mail_gun):
    """Test the service builds the appropriate url"""
    exp = f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}"

    assert mail_gun.base_url == exp


def test_from_flask_app(app):
    mail_gun = MailGunService.from_flask_app(app, test_mode=False)
    assert mail_gun.domain == MAILGUN_DOMAIN
    assert mail_gun.api_key == MAILGUN_API_KEY
    assert mail_gun.test_mode is False
    assert mail_gun.base_url == f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}"


@pytest.mark.parametrize("attr, exp", [("messages_url", f"{BASE_URL}/messages")])
def test_urls(attr, exp, mail_gun):
    assert getattr(mail_gun, attr) == exp


def test_post(mail_gun):
    mocked_client = mail_gun.client

    _ = mail_gun._post("some_url", MultiDict({"test": "data", "o:testmode": "yes"}))

    mocked_client.post.assert_called_with(
        url="some_url", auth=("api", MAILGUN_API_KEY), data=MultiDict({"test": "data", "o:testmode": "yes"})
    )


def test_send_email_raises_value_error(mail_gun):
    call_kwargs = dict(to="anyone", subject="something", from_=None, text="some message", data=None)
    with pytest.raises(ValueError, match=r"sender can not.*"):
        _ = mail_gun.send_mail(**call_kwargs)


@pytest.mark.parametrize("inp", [
    {"html": "some html", "text": "some text"},
    {"html": "some_html", "text": None},
    {"html": None, "text": "some text"}
], ids=["both html and text", "html only", "text only"])
def test_send_email_call(inp, mail_gun):
    call_kwargs = dict(to="anyone", subject="something", from_=None, data=None, **inp)

    mail_gun.default_sender = MAILGUN_DEFAULT_SENDER

    mail_gun.send_mail(**call_kwargs)

    exp_data = MultiDict()

    exp_data["from"] = MAILGUN_DEFAULT_SENDER
    exp_data["to"] = [call_kwargs["to"]]
    exp_data["subject"] = call_kwargs["subject"]
    exp_data["o:testmode"] = "yes"

    if inp["html"]:
        exp_data["html"] = call_kwargs["html"]

    if inp["text"]:
        exp_data["text"] = call_kwargs["text"]

    mail_gun.client.post.assert_called_with(
        url=mail_gun.messages_url, auth=("api", MAILGUN_API_KEY), data=exp_data,
    )
