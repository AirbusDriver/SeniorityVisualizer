from datetime import date, datetime, timedelta
from random import shuffle
from typing import List

import pytest

from seniority_visualizer_app.seniority.models import (
    Pilot,
    PilotRecord,
    SeniorityList,
    SeniorityListRecord,
)
from tests.factories import PilotFactory, PilotRecordFactory


@pytest.fixture
def populated_seniority_list(db):
    """
    Return a SeniorityListRecord with 100 PilotRecords added to it
    """
    published = datetime.utcnow()
    seniority_list = SeniorityListRecord(published, company_name="TestingAir")

    pilot_records = PilotRecordFactory.build_batch(100)

    pilot_records.sort(key=lambda p: (p.hire_date, p.retire_date))

    for i, pilot_rec in enumerate(pilot_records):
        pilot_rec.literal_seniority_number = i + 1
        pilot_rec.seniority_list = seniority_list

    db.session.add_all(pilot_records)
    db.session.commit()

    yield seniority_list

    PilotRecordFactory.reset_sequence()


def test_populated_seniority_list_fixture(populated_seniority_list):
    """Verify populated_seniority_list fixture_behaving predictably."""
    pilots = populated_seniority_list.pilots

    assert len(pilots) == 100

    for a, b in zip(pilots[:-1], pilots[1:]):
        assert a.hire_date <= b.hire_date and a.retire_date <= b.retire_date
        assert a.seniority_list.id == populated_seniority_list.id == 1


def test_seniority_list_from_csv_fixture(seniority_list_from_csv):
    """Verify seniority_list_from_csv fixture behaving predictably."""
    sen_list_record = seniority_list_from_csv

    assert len(sen_list_record.pilots) == 3925


class TestSeniorityListRecord:
    def test_seniority_list_empty_instantiation(self, db):
        """
        Given a SeniorityList instance is saved to db
        When a query on the model is run
        Then the retrieved SeniorityList instance properties are equal to the initial instance
        """

        pub_date = datetime.utcnow()

        sen_list = SeniorityListRecord(published_date=pub_date)

        sen_list.save()

        retrieved = SeniorityListRecord.query.all()[0]

        assert retrieved.id == sen_list.id == 1
        assert retrieved.published_date == sen_list.published_date == pub_date


class TestPilotRecord:
    def test_pilot_record_instantiation_and_retrieval(self, db):
        pilot_record = PilotRecordFactory()

        assert pilot_record.employee_id == "00001"
        assert pilot_record.literal_seniority_number == 1

        pilot_record.update(literal_seniority_number=2)
        assert pilot_record.literal_seniority_number == 2

        assert PilotRecord.query.all()[0].employee_id == pilot_record.employee_id


class TestPilot:
    def test_pilot_is_senior_to(self):
        """
        Given two pilots, pilot1 hired before pilot2
        Then the first pilot is considered senior
        """
        pilot1: Pilot = PilotFactory(hire_date=date(1990, 1, 1))
        pilot2: Pilot = PilotFactory(hire_date=date(1991, 1, 1))

        assert pilot1.is_senior_to(pilot2)
        assert not pilot2.is_senior_to(pilot1)

        """
        Given two pilots hired on the same day
        And the second pilot retires after the first pilot
        Then the pilot retiring before the other pilot is considered more senior
        """
        pilot1.retire_date = date(2000, 1, 1)
        pilot2.hire_date = date(1990, 1, 1)
        pilot2.retire_date = date(2001, 1, 1)

        assert pilot1.is_senior_to(pilot2)
        assert not pilot2.is_senior_to(pilot1)

        """
        Given two pilots hired on the same day
        And the second pilot retires on the same day as the first
        And the second pilot has a higher literal seniority number assigned
        Then pilot1 is considered more senior
        """
        hd = date(1990, 1, 1)
        rd = date(2000, 1, 1)
        pilot1 = PilotFactory(hire_date=hd, retire_date=rd, literal_seniority_number=1)
        pilot2 = PilotFactory(hire_date=hd, retire_date=rd, literal_seniority_number=2)

        assert pilot1.is_senior_to(pilot2)
        assert not pilot2.is_senior_to(pilot1)

        """
        Given two pilots hired on the same day
        And the second pilot retires on the same day as the first
        And the second pilot does not have a literal seniority number assigned
        Then pilot1 is considered more senior
        """
        pilot2.literal_seniority_number = None

        assert pilot1.is_senior_to(pilot2)
        assert not pilot2.is_senior_to(pilot1)

    def test_pilot_hashing(self):
        pilots = PilotFactory.build_batch(10)

        pilot1 = pilots[0]

        p_set = set(pilots)

        assert pilot1 in pilots
        assert pilot1 in p_set
        assert len(p_set) == 10
        assert pilot1 is not pilots[1]

    def test_pilot_ordering(self):
        pilots: List[Pilot] = PilotFactory.build_batch(10)
        copied = pilots.copy()

        assert copied == pilots
        assert sorted(pilots) == pilots

        shuffle(pilots)

        assert not pilots == copied
        assert sorted(pilots) == copied

    def test_pilot_active_on(self):
        hired = date(2020, 1, 1)
        day_before_hired = hired - timedelta(days=1)
        retired = date(2030, 1, 1)
        day_before_retired = retired - timedelta(days=1)

        pilot = PilotFactory(hire_date=hired, retire_date=retired)

        assert not pilot.is_active_on(day_before_hired)
        assert pilot.is_active_on(hired)
        assert pilot.is_active_on(day_before_retired)
        assert not pilot.is_active_on(retired)

    def test_from_dict(self):
        info = {
            "hire_date": datetime(2020, 1, 1),
            "retire_date": datetime(2050, 1, 1),
            "employee_id": "12345",
            "literal_seniority_number": 10,
        }

        new_pilot = Pilot.from_dict(info)

        for k, v in info.items():
            if isinstance(v, datetime):
                v = v.date()
            assert getattr(new_pilot, k) == v


class TestSeniorityList:
    def test_instantiation_with_pilots(self):
        pilots = PilotFactory.build_batch(50)

        sen_list = SeniorityList(pilots)

        assert sen_list._pilots == pilots
        assert set(pilots) == set(sen_list._pilots)

        assert len(sen_list) == 50
        assert "len: 50" in repr(sen_list)

    def test_filter_active_on(self):
        rd = date(2050, 1, 1)
        class_1_hd = date(2000, 1, 1)
        class_2_hd = date(2010, 1, 1)
        class_1 = PilotFactory.build_batch(10, hire_date=class_1_hd, retire_date=rd)
        class_2 = PilotFactory.build_batch(10, hire_date=class_2_hd, retire_date=rd)

        all_pilots = [p for p in class_1]
        all_pilots.extend(class_2)

        sen_list = SeniorityList(all_pilots)

        assert len(set(sen_list.filter_active_on(class_1_hd - timedelta(days=1)))) == 0

        retrieved_class_1 = list(sen_list.filter_active_on(class_1_hd))
        retrieved_class_2 = list(sen_list.filter_active_on(class_2_hd))

        assert set(retrieved_class_1) == set(class_1)
        assert len(retrieved_class_1) == 10

        both = set(retrieved_class_1)
        both.update(set(retrieved_class_2))

        assert both == set(all_pilots)

        assert len(set(sen_list.filter_active_on(date(2060, 1, 1)))) == 0


class TestPilotRecordPilotIntegration:
    def test_to_pilot(self):
        pilot_record = PilotRecordFactory.build()

        pilot = pilot_record.to_pilot()

        assert pilot.hire_date == pilot_record.hire_date.date()
        assert pilot.retire_date == pilot_record.retire_date.date()
        assert pilot.employee_id == pilot_record.employee_id
        assert pilot.literal_seniority_number == pilot_record.literal_seniority_number
