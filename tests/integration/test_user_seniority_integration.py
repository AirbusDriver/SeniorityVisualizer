from datetime import datetime, timedelta
import pytest

from seniority_visualizer_app.seniority.models import SeniorityListRecord, PilotRecord
from seniority_visualizer_app.seniority.views import get_pilot_records_for_employee_id
from tests.factories import PilotRecordFactory, UserFactory


class TestUserPilotRecordLookup:
    def test_user_can_find_pilot_records(self, clean_db):
        sen_list_1 = SeniorityListRecord(datetime.now())
        sen_list_2 = SeniorityListRecord(datetime.now() + timedelta(days=1))

        emp_id = "123"

        record_1 = PilotRecord(employee_id=emp_id, seniority_list=sen_list_1)
        record_2 = PilotRecord(employee_id=emp_id, seniority_list=sen_list_2)
        record_3 = PilotRecord(employee_id="1234", seniority_list=sen_list_1)
        record_1.save()
        record_2.save()
        record_3.save()

        retrieved = get_pilot_records_for_employee_id(emp_id)

        assert len(retrieved) == 2

        assert record_1 in retrieved
        assert record_2 in retrieved
        assert record_3 not in retrieved

        assert get_pilot_records_for_employee_id("test") == []


class TestPilotRecordPilotIntegration:
    def test_to_pilot(self):
        pilot_record = PilotRecordFactory.build()

        pilot = pilot_record.to_entity()

        assert pilot.hire_date == pilot_record.hire_date.date()
        assert pilot.retire_date == pilot_record.retire_date.date()
        assert pilot.employee_id == pilot_record.employee_id
        assert pilot.literal_seniority_number == pilot_record.literal_seniority_number


class TestSeniorityListRecordSeniorityListIntegration:
    def test_to_seniority_list(self, csv_senlist_pilot_records):
        sen_list_record, _ = csv_senlist_pilot_records

        sen_list = sen_list_record.to_entity()

        assert len(sen_list) == len(sen_list_record.pilots)
        assert set(
            p.literal_seniority_number for p in sen_list.pilot_data
        ) == set(
            p.literal_seniority_number for p in sen_list_record.pilots
        )

    def test_to_df(self, csv_senlist_pilot_records):
        sen_list_record, _ = csv_senlist_pilot_records

        df = sen_list_record.to_df()

        assert len(df) == len(sen_list_record.pilots) == 3925
