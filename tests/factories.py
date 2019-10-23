# -*- coding: utf-8 -*-
"""Factories to help in tests."""
from datetime import datetime, timedelta, timezone

from factory import PostGenerationMethodCall, Sequence, LazyAttribute
from factory.fuzzy import FuzzyDateTime, FuzzyChoice
from factory.faker import Faker
from factory.alchemy import SQLAlchemyModelFactory

from seniority_visualizer_app.database import db
from seniority_visualizer_app.user.models import User
from seniority_visualizer_app.seniority.models import PilotRecord


class BaseFactory(SQLAlchemyModelFactory):
    """Base factory."""

    class Meta:
        """Factory configuration."""

        abstract = True
        sqlalchemy_session = db.session


class UserFactory(BaseFactory):
    """User factory."""

    username = Sequence(lambda n: "user{0}".format(n))
    personal_email = Sequence(lambda n: "user{0}@example.com".format(n))
    company_email = Sequence(lambda n: "test.user{0}@jetblue.com".format(n))
    password = PostGenerationMethodCall("set_password", "example")
    active = True

    class Meta:
        """Factory configuration."""

        model = User


class PilotRecordFactory(BaseFactory):
    """PilotRecord row factory."""

    class Meta:
        model = PilotRecord

    employee_id = Sequence(lambda n: str(n + 1).zfill(5))
    hire_date = FuzzyDateTime(
        datetime(2000, 1, 1, tzinfo=timezone.utc),
        force_hour=0,
        force_minute=0,
        force_second=0,
        force_microsecond=0,
    )
    retire_date = LazyAttribute(lambda o: o.hire_date + timedelta(days=(365 * 20)))
    literal_seniority_number = Sequence(lambda n: n + 1)
    first_name = Faker("first_name")
    last_name = Faker("last_name")
    base = FuzzyChoice(["BOS", "JFK", "MCO", "LGB", "FLL"])
    aircraft = FuzzyChoice(["E190", "A320"])
