import pytest

from seniority_visualizer_app.mail.use_cases import usecase_requests


def test_send_company_confirmation_email_request_from_dict():
    BAD_EMAIL = "bad@gmail.com"
    dict_ = {"company_email": BAD_EMAIL}

    res = usecase_requests.SendCompanyConfirmationEmailRequest.from_dict(
        dict_
    )

    exp_param_errors = [
        ("company_email", f"invalid email: {BAD_EMAIL}"),
    ]

    assert not res
    for param, message in exp_param_errors:
        assert {
            "parameter": param,
            "message": message
        } in res.errors

