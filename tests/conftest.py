# -*- coding: utf-8 -*-
"""Defines fixtures available to all tests."""

import logging
from unittest import mock

import pytest
from webtest import TestApp

from seniority_visualizer_app.app import create_app
from seniority_visualizer_app.database import db as _db

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
