import typing as t
from datetime import datetime
from io import StringIO
import uuid
import datetime as dt
import pandas as pd

import pytest

from seniority_visualizer_app.seniority import repo
from seniority_visualizer_app.seniority.models import SeniorityListRecord
from seniority_visualizer_app.seniority.entities import CsvRecord
from tests import factories
from tests.factories import PilotRecordFactory
from tests.settings import CURRENT_SENIORITY_LIST_CSV


@pytest.fixture
def populated_seniority_list(clean_db):
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

    clean_db.session.add_all(pilot_records)
    clean_db.session.commit()

    yield seniority_list

    PilotRecordFactory.reset_sequence()


@pytest.fixture
def csv_record_from_sample_csv() -> CsvRecord:
    record = CsvRecord(
        uuid.uuid4(),
        published=dt.datetime(2010, 1, 1),
        text=CURRENT_SENIORITY_LIST_CSV.read_text()
    )

    return record

@pytest.fixture
def standard_seniority_df(csv_record_from_sample_csv) -> pd.DataFrame:
    """
    Return a standardized dataframe that has lookup access in line with
    SeniorityDfFields attributes. The data is from the sample.csv test csv.


    :param csv_record_from_sample_csv:
    :return:
    """
    from seniority_visualizer_app.seniority import dataframe as loader

    fields = loader.SeniorityDfFields

    buffer = StringIO()
    buffer.write(csv_record_from_sample_csv.text)
    buffer.seek(0)

    df = pd.read_csv(buffer)

    standardized = loader.make_standardized_seniority_dataframe(df, {
        "seniority_number": fields.SENIORITY_NUMBER,
        "cmid": fields.EMPLOYEE_ID,
        "fleet": fields.FLEET,
        "seat": fields.SEAT,
        "base": fields.BASE,
        "retire_date": fields.RETIRE_DATE
    })

    return standardized

@pytest.fixture
def csv_repo_in_memory_factory():
    """
    Return a factory function that returns tuples containing
    a repo and the records within it. Passing an integer to the factory
    sets the number of records the resultant repository will be populated
    with. Those records will also be returned as the last item in the tuple.
    """

    def make_repo(
        records: int = 0
    ) -> t.Tuple[repo.CsvRepoInMemory, t.List[repo.CsvRecord]]:
        csv_records: t.List[repo.CsvRecord] = []
        if records > 0:
            csv_records = factories.CsvRecordFactory.build_batch(records)

        csv_repo = repo.CsvRepoInMemory(records=csv_records)

        return csv_repo, csv_records

    return make_repo
