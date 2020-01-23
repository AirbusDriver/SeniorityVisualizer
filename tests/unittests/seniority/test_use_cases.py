import pytest
from unittest import mock
import datetime as dt
import random

from seniority_visualizer_app.seniority import use_cases as uc
from seniority_visualizer_app.seniority.repo import CsvRepoInMemory
from seniority_visualizer_app.seniority import entities


class TestGetCurrentSeniorityCsv:
    def test_returns_empty(self):
        mock_repo = mock.Mock(autospec=CsvRepoInMemory)

        mock_repo.get_all.return_value = []

        use_case = uc.GetCurrentSeniorityCsv(repo=mock_repo)

        with pytest.raises(ValueError):
            use_case.execute()

    def test_returns_most_recent(self):
        mock_repo = mock.Mock(autospec=CsvRepoInMemory)

        mocked_objs = []

        fake_dates = [dt.datetime(2000 + i, 1, 1) for i in range(10)]

        for d in fake_dates:
            obj = mock.Mock(autospec=entities.CsvRecord)
            obj.published = d
            mocked_objs.append(obj)

        random.shuffle(mocked_objs)

        mock_repo.get_all.return_value = mocked_objs

        use_case = uc.GetCurrentSeniorityCsv(mock_repo)

        result = use_case.execute()

        assert result.published == max(fake_dates)