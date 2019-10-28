from datetime import datetime, timedelta
import pytest

from seniority_visualizer_app.seniority.models import SeniorityListRecord, PilotRecord
from seniority_visualizer_app.seniority.views import get_pilot_records_for_employee_id
from tests.factories import PilotRecordFactory, UserFactory


class TestUserPilotRecordLookup:
    def test_user_can_find_pilot_records(self, db):
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
