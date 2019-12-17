from datetime import datetime, date

from seniority_visualizer_app.seniority.models import PilotRecord, SeniorityListRecord
from seniority_visualizer_app.seniority.entities import SeniorityList, Pilot
from tests.factories import PilotRecordFactory


class TestSeniorityListRecord:
    def test_seniority_list_empty_instantiation(self, clean_db):
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

    def test_from_entity(self, clean_db):
        assert SeniorityListRecord.query.all() == []

        pilots = PilotRecordFactory.build_batch(10)

        sen_list = SeniorityList(published_date=date(2020, 1, 1), pilots=pilots)

        sen_list_record = SeniorityListRecord.from_entity(sen_list)

        sen_list_record.save()

        assert SeniorityListRecord.query.all() == [sen_list_record]


class TestPilotRecord:
    def test_pilot_record_instantiation_and_retrieval(self, clean_db):
        pilot_record = PilotRecordFactory()

        assert pilot_record.employee_id == "00001"
        assert pilot_record.literal_seniority_number == 1

        pilot_record.update(literal_seniority_number=2)
        assert pilot_record.literal_seniority_number == 2

        assert PilotRecord.query.all()[0].employee_id == pilot_record.employee_id


class TestPilotRecordPilotIntegration:
    def test_to_entity(self):
        pilot_record = PilotRecordFactory.build()

        pilot = pilot_record.to_entity()

        assert pilot.hire_date == pilot_record.hire_date.date()
        assert pilot.retire_date == pilot_record.retire_date.date()
        assert pilot.employee_id == pilot_record.employee_id
        assert pilot.literal_seniority_number == pilot_record.literal_seniority_number


class TestSeniorityListRecordSeniorityListIntegration:
    def test_to_entity(self, csv_senlist_pilot_records):
        sen_list_record, _ = csv_senlist_pilot_records

        sen_list = sen_list_record.to_entity()

        assert len(sen_list) == len(sen_list_record.pilots)
        assert set(p.literal_seniority_number for p in sen_list.pilot_data) == set(
            p.literal_seniority_number for p in sen_list_record.pilots
        )

    def test_to_df(self, csv_senlist_pilot_records):
        sen_list_record, _ = csv_senlist_pilot_records

        df = sen_list_record.to_df()

        assert len(df) == len(sen_list_record.pilots)
