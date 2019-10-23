# -*- coding: utf-8 -*-
"""Defines fixtures available to all tests."""

import logging
from unittest import mock
import csv
from pathlib import Path
from datetime import datetime, timezone

import pytest
from webtest import TestApp

from seniority_visualizer_app.app import create_app
from seniority_visualizer_app.database import db as _db
from seniority_visualizer_app.user.role import Role
from seniority_visualizer_app.seniority.models import SeniorityListRecord, PilotRecord

from .factories import UserFactory


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


@pytest.fixture
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


@pytest.fixture
def db(app):
    """Create database for the tests."""
    _db.app = app
    with app.app_context():
        _db.create_all()
        Role.insert_roles()

    yield _db

    # Explicitly close DB connection
    _db.session.close()
    _db.drop_all()


@pytest.fixture
def user(db):
    """Create user for the tests."""
    user = UserFactory(password="myprecious")
    db.session.commit()
    return user


@pytest.fixture
def seniority_list_from_csv(db):
    """
    Return the seniority list populated with records from sample.csv in the test directory
    """
    sample_csv_path = Path(__file__).parent.joinpath("sample.csv")
    assert sample_csv_path.exists()

    sen_list = SeniorityListRecord(published_date=datetime(2000, 1, 1, tzinfo=timezone.utc))
    records = []

    with open(sample_csv_path) as infile:
        reader = csv.DictReader(infile)

        for row in reader:
            record = PilotRecord(
                employee_id=row["cmid"].zfill(5),
                seniority_list=sen_list,
                hire_date=datetime.strptime(row["hire_date"], "%Y-%m-%d"),
                retire_date=datetime.strptime(row["retire_date"], "%Y-%m-%d"),
                literal_seniority_number=int(row["seniority_number"]),
                first_name=row["first_name"],
                last_name=row["last_name"],
                base=row["base"],
                aircraft=row["fleet"],
                seat=row["seat"]
            )
    db.session.add_all(records)
    db.session.add(sen_list)
    db.session.commit()

    return sen_list
