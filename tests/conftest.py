# -*- coding: utf-8 -*-
"""Defines fixtures available to all tests."""

import logging
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock
from typing import Tuple, List

import pytest
from webtest import TestApp

from seniority_visualizer_app.app import create_app
from seniority_visualizer_app.database import db as _db
from seniority_visualizer_app.seniority.models import PilotRecord, SeniorityListRecord
from seniority_visualizer_app.user.role import Role
from seniority_visualizer_app.user.models import User

from .factories import UserFactory
from .utils import make_pilot_dicts_from_csv, log_user_in


def init_db(db):
    """Routine to preload the db"""
    db.create_all()
    Role.insert_roles()

    return db


@pytest.fixture("session")
def patch_mail_id():
    """
    Patch the call to `email.make_msgid` in flask_mail to speed Message() initialization
    up dramatically
    """

    def mock_make_msgid():
        return "<157093746497.29400.9452561162865134712@adder-ws>"

    with mock.patch("flask_mail.make_msgid", side_effect=mock_make_msgid):
        yield


@pytest.fixture(scope="session")
def app(patch_mail_id):
    """Create application for the tests."""
    _app = create_app("tests.settings")
    _app.logger.setLevel(logging.CRITICAL)
    ctx = _app.test_request_context()
    ctx.push()

    yield _app

    ctx.pop()


@pytest.fixture
def testapp(app):
    """Create Webtest app."""
    return TestApp(app)


@pytest.fixture(scope="session")
def session_db(app):
    """Create database for the tests."""

    _db.app = app
    with app.app_context():
        init_db(_db)

    yield _db

    # Explicitly close DB connection
    _db.session.close()
    _db.drop_all()


@pytest.fixture
def clean_db(session_db):
    """Create database for the tests."""
    _db = session_db
    _db.drop_all()

    init_db(_db)

    yield _db

    _db.session.rollback()
    _db.drop_all()


@pytest.fixture
def user(clean_db):
    """Create user for the tests."""
    user = UserFactory(password="myprecious")
    clean_db.session.commit()
    return user


@pytest.fixture(scope="session")
def pilot_dicts_from_csv():
    sample_csv_path = Path(__file__).parent.joinpath("sample.csv")
    assert sample_csv_path.exists()

    pilot_dicts = make_pilot_dicts_from_csv(sample_csv_path)

    return pilot_dicts


# todo: rescope to module level
@pytest.fixture
def csv_senlist_pilot_records(
        clean_db, pilot_dicts_from_csv
) -> Tuple[SeniorityListRecord, List[PilotRecord]]:
    """
    Return Tuple[SeniorityListRecord, List[PilotRecord]]. If the records are needed, they can be saved to `clean_db`
    """

    sen_list = SeniorityListRecord(
        published_date=datetime(2019, 7, 1, tzinfo=timezone.utc)
    )

    records = list(
        PilotRecord(seniority_list=sen_list, **d) for d in pilot_dicts_from_csv
    )

    return sen_list, records


@pytest.fixture
def logged_in_user(testapp, user: User) -> User:
    """
    Return a user that is currently logged into the app.
    """

    password = "myprecious"

    user = log_user_in(user, password, testapp)

    yield user

    user.set_password(password)
    user.save()
    assert user.check_password("myprecious"), "password not set to original password"
