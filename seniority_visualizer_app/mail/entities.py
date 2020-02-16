import typing as t
import logging
from pprint import pformat
from typing import NamedTuple
import abc
from enum import Enum
from werkzeug import MultiDict
from itsdangerous import TimedJSONWebSignatureSerializer, BadSignature, BadTimeSignature

logger = logging.getLogger(__name__)


class MailClientResponse:
    """
    Response from IMailService transaction.
    """

    class ResponseTypes(Enum):
        SUCCESS = "SUCCESS"
        CLIENT_FAIL = "CLIENT_FAIL"
        MAIL_SERVICE_FAIL = "MAIL_SERVICE_FAIL"
        CONNECTION_FAIL = "CONNECTION_FAIL"

    def __init__(self, type_: ResponseTypes, message: str, response: t.Mapping):
        self.type = type_
        self.message = message
        self.response = response

    def __bool__(self):
        return self.type == self.ResponseTypes.SUCCESS

    def __repr__(self):
        s = f"<{type(self).__name__}:({self.type.value}: {self.message})>"
        return s

    @classmethod
    def from_success(cls, response: dict, message: t.Optional[str] = None):
        type_ = cls.ResponseTypes.SUCCESS

        return cls(
            type_=type_,
            message=message or "Email Sent Successfully!",
            response=response,
        )


class IMailService(abc.ABC):
    @abc.abstractmethod
    def send_mail(
        self,
        to: t.Union[str, t.Iterable[str]],
        subject: str,
        from_: t.Optional[str] = None,
        text: t.Optional[str] = None,
        html: t.Optional[str] = None,
        data: MultiDict = None,
    ) -> MailClientResponse:
        """
        Send an email to a recipient, or an iterable of recipients.

        Returns a MailClientResponse containing response generated from the client.

        :param to: recipient or iterable of recipients
        :param subject: subject of email
        :param from_: sender of domain, if ommited, the `default_sender` attribute will be used.
        If it is not set, a ValueError should be raised.
        :param text: text representation of email
        :param html: html representation of email
        :param data: additional mail data.
        :return: MailClientResponse
        """
        raise NotImplementedError()


class Mailer:
    def __init__(self, service: IMailService):
        self.service = service

    def send_mail(
        self,
        to: t.Union[str, t.List[str]],
        subject: str,
        from_: t.Optional[str] = None,
        text: t.Optional[str] = None,
        html: t.Optional[str] = None,
        data: t.Optional[MultiDict] = None,
    ):
        try:
            if text or html:
                logger.info(
                    "\n".join(
                        [
                            f"Trying {self.__class__.__name__}.send_mail()",
                            f"Sending mail using '{type(self.service).__name__}' service",
                        ]
                    )
                )
                response = self.service.send_mail(
                    to=to, subject=subject, from_=from_, text=text, html=html, data=data
                )
                logger.info(
                    "\n".join(
                        [
                            f"MAIL SENT TO -> {to} with subject {subject}",
                            f"RESP: {pformat(getattr(response, '__dict__', {}))}",
                        ]
                    )
                )
            else:
                raise ValueError("text or html must be provided")
        except Exception as e:
            call_data = {
                "to": to,
                "subject": subject,
                "from_": from_,
            }
            logger.error(
                f"Error occurred in mail client using {self.service.__class__.__name__}.send_mail() -> {call_data}"
            )
            logger.exception("EXC: ", exc_info=e)
            return MailClientResponse(
                type_=MailClientResponse.ResponseTypes.CLIENT_FAIL,
                message=f"{type(e).__name__}: {str(e)}",
                response={"messsage": str(e)},
            )
        else:
            return response


class EmailTokenVerificationReason(Enum):
    TIMEOUT = "TIMEOUT"
    SUCCESS = "SUCCESS"
    BAD_TOKEN = "BAD_TOKEN"


class EmailTokenVerificationResponse(NamedTuple):
    """Response types for email token de-serializations"""

    successful: bool
    reason: EmailTokenVerificationReason
    message: str


class EmailTokenizer:
    """
    Tokenizes emails into web-safe tokens that contain the payload needed to verify
    an email. This should instantiated once and used across all email tokenization
    as verification methods and functions.
    """

    reasons = EmailTokenVerificationReason

    def __init__(self, key: str, timeout: int = 3600):
        self.timeout = timeout
        self._serializer = self._make_serializer(key, self.timeout)

    def __repr__(self):
        s = f"<{type(self).__name__}(timeout: {self.timeout})>"
        return s

    @property
    def serializer(self):
        return self._serializer

    @serializer.setter
    def serializer(self, value):
        raise AttributeError("serializer is readonly")

    def _make_serializer(self, key, timout):
        return TimedJSONWebSignatureSerializer(key, timout)

    def create_email_token(self, email) -> str:
        """Return a string containing a web-safe payload from the serializer instance."""
        return self.serializer.dumps(email).decode()

    def verify_email_token(
        self, token: str, email: str, case_insensitive: bool = True
    ) -> EmailTokenVerificationResponse:

        """
        Return a EmailTokenVerificationResponse indicating the validity
        of the email token and why it may be invalid.
        """

        try:
            res = self.serializer.loads(token)
        except BadTimeSignature as e:
            return EmailTokenVerificationResponse(
                successful=False,
                reason=EmailTokenVerificationReason.TIMEOUT,
                message=str(e),
            )
        except BadSignature as e:
            return EmailTokenVerificationResponse(
                successful=False,
                reason=EmailTokenVerificationReason.BAD_TOKEN,
                message=str(e),
            )

        if case_insensitive:
            res = res.lower()
            email = email.lower()

        if res == email:
            return EmailTokenVerificationResponse(
                True, reason=EmailTokenVerificationReason.SUCCESS, message="SUCCESS"
            )
