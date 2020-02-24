import typing as t
import logging
import pprint

import requests
from werkzeug import MultiDict

if t.TYPE_CHECKING:
    from flask import Flask

from .entities import IMailService, MailClientResponse

logger = logging.getLogger(__name__)


class MailGunService(IMailService):
    _BASE_URL = "https://api.mailgun.net/v3/{DOMAIN}"
    _AUTH_USERNAME = "api"
    client = requests

    def __init__(
        self, api_key: str, domain: str, test_mode=False, default_sender: str = None
    ):
        self.api_key = api_key
        self.test_mode = test_mode
        self.domain = domain
        self.default_sender = default_sender

    @property
    def base_url(self) -> str:
        return self._BASE_URL.format(DOMAIN=self.domain)

    @property
    def messages_url(self) -> str:
        return f"{self.base_url}/messages"

    @classmethod
    def from_flask_app(cls, app: "Flask", test_mode: bool = False) -> "MailGunService":
        return cls(
            api_key=app.config["MAILGUN_API_KEY"],
            domain=app.config["MAILGUN_DOMAIN"],
            test_mode=test_mode,
            default_sender=f"B6 Seniority Mail <admin@{app.config['MAILGUN_DOMAIN']}>",
        )

    def send_mail(
        self,
        to: t.Union[str, t.Iterable[str]],
        subject: str,
        from_: t.Optional[str] = None,
        text: t.Optional[str] = None,
        html: t.Optional[str] = None,
        data: MultiDict = None,
    ) -> MailClientResponse:
        d: MultiDict = MultiDict() if data is None else data

        if isinstance(to, str):
            to = [to]

        sender = from_ if from_ is not None else self.default_sender
        if sender is None:
            raise ValueError("sender can not be none if 'default_sender' not set")

        d.add("to", to)
        d.add("subject", subject)
        d.add("from", sender)

        if text:
            d.add("text", text)
        if html:
            d.add("html", html)

        if not (text or html):
            raise ValueError("text or html must be provided")

        res = self._post(self.messages_url, data=d)

        try:
            res_data: dict = res.json()
        except ValueError as e:
            return MailClientResponse(
                type_=MailClientResponse.ResponseTypes.MAIL_SERVICE_FAIL,
                message=str(e),
                response={"value": res},
            )

        return MailClientResponse.from_success(res_data)

    def _post(self, url: str, data: t.Optional[MultiDict] = None, **kwargs):
        data = data or MultiDict()
        if self.test_mode:
            data["o:testmode"] = "yes"
        res = self.client.post(url=url, data=data, auth=("api", self.api_key), **kwargs)
        return res


class NullService(IMailService):
    def send_mail(
        self,
        to: t.Union[str, t.Iterable[str]],
        subject: str,
        from_: t.Optional[str] = None,
        text: t.Optional[str] = None,
        html: t.Optional[str] = None,
        data: t.Optional[MultiDict] = None,
    ) -> MailClientResponse:
        call_data = {
            "to": to,
            "subject": subject,
            "from_": from_,
            "text": text,
            "html": html,
            "data": data,
        }

        msg = f"'send_mail' called with data: \n{pprint.pformat(call_data)}"

        logger.info(msg)

        response = MailClientResponse(
            type_=MailClientResponse.ResponseTypes.SUCCESS, message=msg, response=data
        )

        return response
