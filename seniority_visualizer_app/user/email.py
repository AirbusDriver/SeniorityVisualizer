import threading

from flask import render_template, url_for
from flask_mail import Message
from itsdangerous import jws, TimedJSONWebSignatureSerializer

from flask import current_app


def make_email_serializer(timeout=3600) -> TimedJSONWebSignatureSerializer:
    email_serializer = jws.TimedJSONWebSignatureSerializer(
        current_app.config["SECRET_KEY"], expires_in=timeout
    )
    return email_serializer


def send_email(message, app):
    """Send an email message"""


def async_send_email(message, app):
    """Send email message in background"""


def send_confirmation_email(user, email, token):
    """Send a confirmation email with timout."""

    # generate token using email_type and user id

    # make url using that token

    # render the html with that url

    # render the text email with that url

    # construct the message

    # send message in background thread
