"""Settings module for test app."""
from pathlib import Path
import datetime as dt

TESTS_DIR = Path(__file__).parent

ENV = "development"
TESTING = True
SQLALCHEMY_DATABASE_URI = "sqlite://"
SECRET_KEY = "not-so-secret-in-tests"
BCRYPT_LOG_ROUNDS = (
    4
)  # For faster tests; needs at least 4 to avoid "ValueError: Invalid rounds"
DEBUG_TB_ENABLED = False
CACHE_TYPE = "simple"  # Can be "memcached", "redis", etc.
SQLALCHEMY_TRACK_MODIFICATIONS = False
WEBPACK_MANIFEST_PATH = "webpack/manifest.json"
WTF_CSRF_ENABLED = False  # Allows form testing

MAIL_USERNAME = "admin_mail@example.com"
MAIL_DEFAULT_SENDER = "admin_mail@example.com"
MAIL_PASSWORD = "1122boogiewoogieave"
MAIL_SERVER = "localhost"
MAIL_PORT = "123"
MAIL_USE_SSL = True

CURRENT_SENIORITY_LIST_CSV = TESTS_DIR / "sample.csv"
CURRENT_SENIORITY_LIST_PUBLISHED = dt.datetime(2020, 1, 1)
