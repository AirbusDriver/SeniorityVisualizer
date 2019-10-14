import threading

from flask import render_template, url_for, current_app
from flask_mail import Message
from itsdangerous import jws, TimedJSONWebSignatureSerializer

from seniority_visualizer_app.extensions import mail


def make_email_serializer(timeout=3600) -> TimedJSONWebSignatureSerializer:
    email_serializer = jws.TimedJSONWebSignatureSerializer(
        current_app.config["SECRET_KEY"], expires_in=timeout
    )
    return email_serializer


def send_async_email(message: Message, app):
    """Send an email message"""
    with app.app_context():
        current_app.logger.info(f"SENDING MESSAGE")
        mail.send(message)
        current_app.logger.info(f"SENT {message.subject} to {message.recipients}")


def send_email(message):
    """Send email message in background"""
    app_obj = current_app._get_current_object()
    thread = threading.Thread(target=send_async_email, args=(message, app_obj))
    thread.start()

    return thread


def send_confirmation_email(user: "User", email_category):
    """Send a confirmation email with timout."""

    token = user.generate_confirmation_token(email_category)

    url = url_for("user.confirm_user", token=token, _external=True)

    html = render_template("mail/confirmation.html", confirmation_url=url)

    text = render_template("mail/confirmation.txt", confirmation_url=url)

    # construct the message
    msg = Message()
    msg.subject = "Please confirm your email."
    msg.html = html
    msg.body = text
    msg.recipients.append(getattr(user, email_category.value))

    # send message in background thread
    send_email(msg)
    return url


def send_password_reset_token(user: "User", email_category, reset_url):
    """Send a password reset email with timeout."""
    recipient = getattr(user, email_category.value)

    html = render_template("mail/reset_password.html", url=reset_url)
    text = render_template("mail/reset_password.txt", url=reset_url)

    msg = Message()
    msg.subject = "Reset your password."
    msg.html = html
    msg.body = text
    msg.recipients.append(recipient)

    current_app.logger.info(f"EMAIL RESET -> sent to {recipient}")

    send_email(msg)


def _prep_email(s):
    """Tokenize email for comparison"""
    return s.lower().strip()


def compare_emails(email_1, email_2):
    """Return True if email_1 and email_2 are effectively equal"""
    return _prep_email(email_1) == _prep_email(email_2)
