import enum
import re

from wtforms.validators import Email, ValidationError

EMPLOYEE_NUMBER_EMAIL_PATTERN_PREFIX = r"^\w{2,3}\d{1,5}"
EMPLOYEE_NAME_EMAIL_PATTERN_PREFIX = r"^\S+"
HOST = "@jetblue.com$"

long_employee_email_pattern = EMPLOYEE_NAME_EMAIL_PATTERN_PREFIX + HOST
short_employee_email_pattern = EMPLOYEE_NUMBER_EMAIL_PATTERN_PREFIX + HOST

long_company_email_regex = re.compile(long_employee_email_pattern, re.I)
short_company_email_regex = re.compile(short_employee_email_pattern, re.I)


# todo: employee number validator


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


class UniqueField:
    def __init__(self, model, attr, message=None):
        self.message = message or "Already registered"
        self.model = model
        self.attr = attr

    def __call__(self, form, field):
        data = field.data

        query = {self.attr: data}

        if self.model.query.filter_by(**query).first():
            raise ValidationError(self.message)

        return True
