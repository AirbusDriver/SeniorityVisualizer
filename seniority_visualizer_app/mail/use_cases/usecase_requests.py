import re

from seniority_visualizer_app.shared.request_object import InvalidRequestObject, ValidRequestObject, UseCaseRequest
from seniority_visualizer_app.user.validators import CompanyEmail


def validate_company_email(email: str):
    if CompanyEmail.is_valid_email(email):
        return email
    else:
        raise ValueError(f"invalid email: {email}")


class SendCompanyConfirmationEmailRequest(UseCaseRequest):

    def __init__(self, company_email: str, timeout: int = 3600):
        self.company_email = company_email
        self.timeout = timeout

    @classmethod
    def from_dict(cls, dict_: dict) -> UseCaseRequest:
        invalid = InvalidRequestObject()
        try:
            email = cls.validate_company_email(dict_["company_email"])
        except ValueError as e:
            invalid.add_error("company_email", str(e))
            email = str(dict_.get("company_email"))

        timeout = dict_.get("timeout")

        if not timeout or int(timeout) < 60:
            invalid.add_error("timeout", "timeout required to be an int greater than 60")

        timeout = int(timeout)

        if invalid.has_errors():
            return invalid

        return cls(
            company_email=email,
            timeout=timeout
        )

    @classmethod
    def validate_company_email(cls, email: str) -> str:
        return validate_company_email(email)
