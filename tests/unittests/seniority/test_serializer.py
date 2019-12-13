import datetime as dt
from unittest import mock

import pytest

from seniority_visualizer_app.seniority import serializer
from seniority_visualizer_app.seniority.entities import Pilot, SeniorityList

from tests.factories import PilotFactory


@pytest.mark.parametrize(
    "inp, exp",
    [
        (SeniorityList, serializer.SeniorityListSerializer),
        (SeniorityList(), serializer.SeniorityListSerializer),
        (Pilot, serializer.PilotSerializer),
        (PilotFactory(), serializer.PilotSerializer),
    ],
)
def test_get_serializer(inp, exp):
    assert serializer.get_serializer(inp) == exp


class TestPilotSerializer:
    def test_to_dict(self):
        pilot = Pilot(
            employee_id="123",
            hire_date=dt.date(2000, 1, 1),
            retire_date=dt.date(2020, 1, 1),
            literal_seniority_number=1,
        )

        exp = dict(
            employee_id="123",
            hire_date=dt.date(2000, 1, 1),
            retire_date=dt.date(2020, 1, 1),
            literal_seniority_number=1,
        )

        serialized = serializer.PilotSerializer().to_dict(pilot)

        assert serialized == exp


class TestSeniorityListSerializer:
    def test_to_dict(self):
        PilotFactory.reset_sequence()

        pilots = PilotFactory.build_batch(100)

        sen_list = SeniorityList(pilots=pilots, published_date="2000-1-15")

        sen_serializer = serializer.SeniorityListSerializer()

        serialized = sen_serializer.to_dict(sen_list)

        assert list(serialized.keys()) == ["pilots", "published_date"]
        assert len(serialized["pilots"]) == 100
        assert serialized["published_date"] == dt.date(2000, 1, 15)
