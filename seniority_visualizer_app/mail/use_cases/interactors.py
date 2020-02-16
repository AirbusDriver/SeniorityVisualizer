import logging

from seniority_visualizer_app.shared import UseCase, ResponseSuccess, ResponseFailure
from seniority_visualizer_app.mail.entities import MailClientResponse, Mailer, EmailTokenizer
from .usecase_requests import SendCompanyConfirmationEmailRequest


logger = logging.getLogger(__name__)


class SendConfirmationEmailUseCase(UseCase):

    def __init__(self, mailer: Mailer):
        self.mailer = mailer

    def process_request(self, request_object: SendCompanyConfirmationEmailRequest):
        mail_response = self.mailer.send_mail(
            request_object.company_email,
            "Please confirm your company email to continue!",
            text=f"Please confirm your email by following this link. \n\n{request_object.verification_link}"
        )

        if mail_response.type == mail_response.ResponseTypes.SUCCESS:
            return ResponseSuccess(
                value=mail_response.message
            )

        else:
            if mail_response.type == mail_response.ResponseTypes.CLIENT_FAIL:
                return ResponseFailure.build_parameters_error(mail_response.message)