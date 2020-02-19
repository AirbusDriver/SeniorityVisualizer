# -*- coding: utf-8 -*-
"""Application configuration.

Most configuration is set via environment variables.

For local development, use a .env file to set
environment variables.
"""
from environs import Env

env = Env()
env.read_env()

FLASK_ADMIN = env.str("FLASK_ADMIN")

ENV = env.str("FLASK_ENV", default="production")
DEBUG = ENV == "development"
SQLALCHEMY_DATABASE_URI = env.str("DATABASE_URL")
SECRET_KEY = env.str("SECRET_KEY")
BCRYPT_LOG_ROUNDS = env.int("BCRYPT_LOG_ROUNDS", default=13)
DEBUG_TB_ENABLED = DEBUG
DEBUG_TB_INTERCEPT_REDIRECTS = False
CACHE_TYPE = "simple"  # Can be "memcached", "redis", etc.
SQLALCHEMY_TRACK_MODIFICATIONS = False
WEBPACK_MANIFEST_PATH = "webpack/manifest.json"
SERVER_NAME = env.str("SERVER_NAME", default="0.0.0.0:5000")

MAIL_USERNAME = env.str("MAIL_USERNAME")
MAIL_DEFAULT_SENDER = env.str("MAIL_DEFAULT_SENDER", default=None)
MAIL_PASSWORD = env.str("MAIL_PASSWORD")
MAIL_SERVER = env.str("MAIL_SERVER")
MAIL_PORT = env.int("MAIL_PORT")
MAIL_USE_SSL = True
MAIL_SUPPRESS_SEND = env.bool("MAIL_SUPPRESS_SEND", default=True)
MAIL_TOKEN_TIMEOUT = 3600

MAILGUN_API_KEY = env.str("MAILGUN_API_KEY")
MAILGUN_DOMAIN = env.str("MAILGUN_DOMAIN")
MAILGUN_PUBLIC_KEY = env.str("MAILGUN_PUBLIC_KEY")

CURRENT_SENIORITY_LIST_CSV = env.path("CURRENT_SENIORITY_LIST_CSV")
CURRENT_SENIORITY_LIST_PUBLISHED = env.date("CURRENT_SENIORITY_LIST_PUBLISHED")
