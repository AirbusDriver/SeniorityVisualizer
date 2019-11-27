from datetime import datetime

import pytest

from seniority_visualizer_app.seniority.models import SeniorityListRecord
from tests.factories import PilotRecordFactory


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