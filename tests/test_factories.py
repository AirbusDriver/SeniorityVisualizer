import datetime as dt

import pytest

from . import factories


def test_pilot_factory():
    pilot = factories.PilotFactory()

    assert pilot.employee_id == "00001"
    assert pilot.literal_seniority_number == 1
    assert pilot.hire_date == dt.date(1990, 1, 1)
    assert pilot.retire_date == dt.date(2030, 1, 1)


def test_pilot_factory_batch():
    pilots = factories.PilotFactory.build_batch(10)

    assert [p.literal_seniority_number for p in pilots] == list(range(1, 11))
    assert {p.hire_date for p in pilots} == {dt.date(1990, 1, 1), dt.date(1991, 1, 1)}
