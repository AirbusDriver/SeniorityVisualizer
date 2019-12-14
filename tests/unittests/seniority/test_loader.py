import datetime as dt
from pathlib import Path

import pytest

from ...utils import SAMPLE_CSV

from seniority_visualizer_app.seniority.loader import SeniorityListLoader


@pytest.fixture
def sample_csv_loader():
    headers = {
            "seniority_number": "literal_seniority_number",
            "cmid": "employee_id",
        }

    loader = SeniorityListLoader(headers=headers)

    return loader


class TestSeniorityLoader:
    def test_rename_keys(self):
        inp = {"test": "check1", "one": "check2", "two": "check3"}

        headers = {"one": "five"}

        assert SeniorityListLoader.rename_keys(inp, headers) == {
            "test": "check1",
            "five": "check2",
            "two": "check3",
        }

    def test_load_stream_to_dicts(self, tmp_path: Path):
        csv_ = """col1,col2,col3\na,b,c\nd,e,f"""

        fp = tmp_path.joinpath("tmp_csv.csv")
        fp.write_text(csv_)

        data = SeniorityListLoader()._load_stream_to_dicts(fp.open())

        assert data == [
            {"col1": "a", "col2": "b", "col3": "c"},
            {"col1": "d", "col2": "e", "col3": "f"},
        ]

    def test_load_from_stream(self, sample_csv_loader):
        sen_list = sample_csv_loader.load_from_stream(
            Path(SAMPLE_CSV).open(), published_date="2000-1-1"
        )

        assert sen_list.published_date == dt.date(2000, 1, 1)
        assert len(sen_list.pilot_data) == 3925
