import pytest
import uuid

from seniority_visualizer_app.mail.entities import MailClientResponse


def test_success():
    response = {
        "status": 200,
        "id": uuid.uuid4(),
    }

    client_response = MailClientResponse.from_success(response)

    assert bool(client_response)
    assert client_response.message == "Email Sent Successfully!"
    assert client_response.response == response


def test_client_failure():
    response = {
        "status": 401,
        "message": "credentials failure"
    }

    client_response = MailClientResponse(type_=MailClientResponse.ResponseTypes.CLIENT_FAIL,
                                         message=response["message"], response=response)

    assert not bool(client_response)