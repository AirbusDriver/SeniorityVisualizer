import re
import enum

from wtforms.validators import Email
from wtforms.validators import ValidationError


EMPLOYEE_NUMBER_EMAIL_PATTERN_PREFIX = r"^\w{2,3}\d{1,5}"
EMPLOYEE_NAME_EMAIL_PATTERN_PREFIX = r"^\S+"
HOST = "@jetblue.com$"

long_employee_email_pattern = EMPLOYEE_NAME_EMAIL_PATTERN_PREFIX + HOST
short_employee_email_pattern = EMPLOYEE_NUMBER_EMAIL_PATTERN_PREFIX + HOST

long_company_email_regex = re.compile(long_employee_email_pattern, re.I)
short_company_email_regex = re.compile(short_employee_email_pattern, re.I)


class EmailValidationRegexEnum(enum.Enum):
    LONG_EMAIL = long_company_email_regex
    SHORT_EMAIL = short_company_email_regex


class CompanyEmail(Email):
    def __init__(self, message=None):
        message = message or "Email is not a valid company email."
        super().__init__(message)

    def __call__(self, form, field):
        email_string = field.data

        if self.is_valid_email(email_string):
            return True
        else:
            raise ValidationError(self.message)

    @staticmethod
    def is_valid_email(email) -> bool:
        """Return True if is valid company email"""
        try:
            for validation_regex in EmailValidationRegexEnum:
                match = validation_regex.value.match(email)
                if match:
                    return True
            else:
                return False
        except TypeError:
            return False
