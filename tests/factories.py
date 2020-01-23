# -*- coding: utf-8 -*-
"""Factories to help in tests."""
import math
from datetime import date, datetime, timedelta, timezone
import uuid

from factory import Factory, LazyAttribute, PostGenerationMethodCall, Sequence, sequence, LazyFunction
from factory.alchemy import SQLAlchemyModelFactory
from factory.faker import Faker
from factory.fuzzy import FuzzyChoice, FuzzyDateTime
import faker

from seniority_visualizer_app.database import db
from seniority_visualizer_app.seniority.models import PilotRecord
from seniority_visualizer_app.seniority.entities import Pilot, CsvRecord
from seniority_visualizer_app.user.models import User

fake = faker.Faker()

def make_sample_csv_text():
    headers = ",".join(["first", "last", "date", "num"])

    fake = faker.Faker()

    def make_row():
        row = [
            fake.first_name(),
            fake.last_name(),
            fake.date(),
            str(fake.random_int())
        ]
        return ",".join(row)

    rows = "\n".join(make_row() for _ in range(20))

    csv_text = headers + "\n" + rows

    return csv_text




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
    employee_id = Sequence(lambda n: n + 1)

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


class PilotFactory(Factory):
    """Pilot factory"""

    class Meta:
        model = Pilot

        inline_args = ("employee_id", "hire_date", "retire_date")

    employee_id = Sequence(lambda n: str(n + 1).zfill(5))
    literal_seniority_number = Sequence(lambda n: n + 1)

    @sequence
    def hire_date(n) -> date:
        """Hire dates group by five starting 1990-01-01 and increment by year after each five pilots."""
        class_num = math.floor(n / 5)
        year = class_num + 1990
        return date(year, 1, 1)

    @sequence
    def retire_date(n) -> date:
        """Retirements start at 2030-01-01 and increment a month per pilot"""
        retirements_start = date(2030, 1, 1)

        adj_year, adj_month = divmod(n, 12)

        return date(
            retirements_start.year + adj_year, retirements_start.month + adj_month, 1
        )


class CsvRecordFactory(BaseFactory):
    """CsvRecord Factory"""

    class Meta:
        model = CsvRecord

        inline_args = ("id", "published", "text")

    id = LazyFunction(lambda: uuid.uuid4())
    published = LazyFunction(lambda: datetime.fromisoformat(fake.date()))
    text = LazyFunction(make_sample_csv_text)
