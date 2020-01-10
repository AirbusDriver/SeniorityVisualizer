import datetime as dt
from unittest import mock
import json

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

    def test_to_json(self):
        pilot = Pilot(
            employee_id="123",
            hire_date=dt.date(2000, 1, 1),
            retire_date=dt.datetime(2020, 1, 1),
            literal_seniority_number=1,
        )

        json_string = serializer.PilotSerializer().to_json(pilot)

        unpacked = json.loads(json_string)

        assert unpacked["hire_date"] == "2000-01-01"
        assert unpacked["retire_date"] == "2020-01-01"
        assert unpacked["literal_seniority_number"] == 1
        assert unpacked["employee_id"] == "123"


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

    def test_to_df(self, csv_senlist_pilot_records):
        sen_list_record, _ = csv_senlist_pilot_records

        df = serializer.SeniorityListSerializer().to_df(sen_list_record.to_entity())

        assert len(df) == len(sen_list_record.pilots) == 3925
