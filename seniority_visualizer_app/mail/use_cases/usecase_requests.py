from seniority_visualizer_app.shared.request_object import InvalidRequestObject, ValidRequestObject, UseCaseRequest
from seniority_visualizer_app.user.validators import CompanyEmail


def validate_company_email(email: str):
    if CompanyEmail.is_valid_email(email):
        return email
    else:
        raise ValueError(f"invalid email: {email}")


class SendCompanyConfirmationEmailRequest(UseCaseRequest):

    def __init__(self, company_email: str, verification_link: str):
        self.company_email = company_email
        self.verification_link = verification_link

    @classmethod
    def from_dict(cls, dict_: dict) -> UseCaseRequest:
        invalid = InvalidRequestObject()
        try:
            email = cls.validate_company_email(dict_["company_email"])
        except ValueError as e:
            invalid.add_error("company_email", str(e))
            email = str(dict_.get("company_email"))

        try:
            pre_checked_link = dict_.get("verification_link", "")
            cls.validate_verification_link(pre_checked_link)
        except Exception as e:
            invalid.add_error("verification_link", str(e))
        finally:
            link = pre_checked_link

        if invalid.has_errors():
            return invalid

        return cls(
            company_email=email,
            verification_link=link
        )

    @classmethod
    def validate_company_email(cls, email: str) -> str:
        return validate_company_email(email)

    @classmethod
    def validate_verification_link(cls, link: str) -> str:
        return link
