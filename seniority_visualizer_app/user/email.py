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


def send_async_email(message, app):
    """Send an email message"""
    with app.app_context():
        print(f"SENDING MESSAGE")
        mail.send(message)
        print(f"SENT {vars(message)}")


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
