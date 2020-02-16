from seniority_visualizer_app.mail.entities import EmailTokenizer, Mailer
from seniority_visualizer_app.mail.adapters import NullService, MailGunService


def get_current_flask_app_email_tokenizer() -> EmailTokenizer:
    """Make an EmailTokenizer from the current app configuration"""
    from flask import current_app

    timeout = int(current_app.config.get("MAIL_TOKEN_TIMEOUT", 3600))
    key = current_app.config["SECRET_KEY"]

    serializer = EmailTokenizer(
        key=key,
        timeout=timeout
    )

    return serializer


def get_current_flask_app_mailer() -> Mailer:
    from flask import current_app

    config = current_app.config

    if config.get("MAIL_SUPPRESS_SEND") or config.get("TESTING"):

        mailer = Mailer(NullService())

    else:

        service = MailGunService(
            api_key=config["MAILGUN_API_KEY"],
            domain=config["MAILGUN_DOMAIN"],
            test_mode=False,
            default_sender=f"Account Management <{config['MAILGUN_DOMAIN']}>"
        )

        mailer = Mailer(service=service)

    return mailer
