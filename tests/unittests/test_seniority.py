from datetime import datetime, date

import pytest

from seniority_visualizer_app.seniority.models import (
    SeniorityListRecord,
    PilotRecord,
    Pilot,
)
from tests.factories import PilotRecordFactory, PilotFactory


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
