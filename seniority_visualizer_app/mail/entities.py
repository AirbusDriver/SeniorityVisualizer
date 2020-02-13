import typing as t
import abc
from enum import Enum
from werkzeug import MultiDict


class MailClientResponse:
    """
    Response from IMailService transaction.


    """

    class ResponseTypes(Enum):
        SUCCESS = "SUCCESS"
        CLIENT_FAIL = "CLIENT_FAIL"
        MAIL_SERVICE_FAIL = "MAIL_SERVICE_FAIL"
        CONNECTION_FAIL = "CONNECTION_FAIL"

    def __init__(self, type_: ResponseTypes, message: str, response: t.Dict):
        self.type = type_
        self.message = message
        self.response = response

    def __bool__(self):
        return self.type == self.ResponseTypes.SUCCESS

    def __repr__(self):
        s = f"<{type(self):({self.type.value}: {self.message})}>"
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
            from_: t.Optional[str],
            text: t.Optional[str] = None,
            html: t.Optional[str] = None,
            data: t.Optional[MultiDict] = None,
    ):
        try:
            if text or html:
                response = self.service.send_mail(
                    to=to,
                    subject=subject,
                    from_=from_,
                    text=text,
                    html=html,
                    data=data
                )
            else:
                raise ValueError(
                    "text or html must be provided"
                )
        except Exception as e:
            return MailClientResponse(
                type_=MailClientResponse.ResponseTypes.CLIENT_FAIL,
                message=f"{type(e).__name__}: {str(e)}",
                response={
                    "messsage": str(e)
                }
            )
        else:
            return response
