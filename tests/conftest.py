# -*- coding: utf-8 -*-
"""Defines fixtures available to all tests."""

import csv
import logging
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

import pytest
from webtest import TestApp
from flask import url_for

from seniority_visualizer_app.app import create_app
from seniority_visualizer_app.database import db as _db
from seniority_visualizer_app.seniority.models import PilotRecord, SeniorityListRecord
from seniority_visualizer_app.user.role import Role
from seniority_visualizer_app.user.models import User

from .factories import UserFactory
from .utils import make_seniority_list_from_csv


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


# todo: rescope to module level
@pytest.fixture
def seniority_list_from_csv(db):
    """
    Return the seniority list populated with records from sample.csv in the test directory
    """
    sample_csv_path = Path(__file__).parent.joinpath("sample.csv")
    assert sample_csv_path.exists()

    sen_list, records = make_seniority_list_from_csv(sample_csv_path)
    db.session.add_all(records)
    db.session.add(sen_list)
    db.session.commit()

    return sen_list


@pytest.fixture
def logged_in_user(testapp, user: User) -> User:
    """
    Return a user that is currently logged into the app.
    """
    res = testapp.get(url_for("public.home"))
    form = res.forms["loginForm"]
    form["username"] = user.username
    form["password"] = "myprecious"

    res = form.submit().maybe_follow()
    assert res.status_code == 200, "user unable to log in"

    yield user

    user.set_password("myprecious")
    user.save()
    assert user.check_password("myprecious"), "password not set to original password"
