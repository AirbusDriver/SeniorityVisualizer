import pytest
from unittest import mock
import datetime as dt
import random

import pandas as pd

from seniority_visualizer_app.seniority import use_cases as uc
from seniority_visualizer_app.seniority.repo import CsvRepoInMemory
from seniority_visualizer_app.seniority import entities


class TestGetCurrentSeniorityCsv:
    def test_returns_empty(self):
        mock_repo = mock.Mock(autospec=CsvRepoInMemory)

        mock_repo.get_all.return_value = []

        req = uc.requests.SeniortyFilterRequest()

        use_case = uc.GetCurrentSeniorityCsv(repo=mock_repo)

        res = use_case.execute(req)

        assert res.type == uc.ResponseSuccess.SUCCESS
        assert res.value == []

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

        req = uc.requests.SeniortyFilterRequest(most_recent=True)

        use_case = uc.GetCurrentSeniorityCsv(mock_repo)

        response = use_case.execute(req)

        assert response.value.published == max(fake_dates)


class TestGetCurrentSeniorityListReport:
    def test_execute(self, standard_seniority_df, csv_record_from_sample_csv):
        mock_repo = mock.MagicMock()
        mock_repo.get_all.return_value = [csv_record_from_sample_csv]

        def df_factory(_):
            return standard_seniority_df

        with mock.patch("seniority_visualizer_app.seniority.use_cases.dt") as mock_dt:
            mock_dt.datetime.now.return_value = dt.datetime(2020, 2, 7)

            req = uc.requests.SeniorityReportRequest(use_current=True)

            res = (
                uc.GetCurrentSeniorityListReport(mock_repo, df_factory)
                .execute(req)
                .value
            )

        assert res.valid_date == dt.datetime(2010, 1, 1)
        assert res.total_pilots == 3925
        assert res.span == (res.valid_date, dt.datetime(2059, 5, 1))
        assert res.total_retired == 14

    def test_execution_failure(self, standard_seniority_df, csv_record_from_sample_csv):
        mock_repo = mock.MagicMock()
        mock_df_factory = mock.MagicMock()

        with mock.patch(
            "seniority_visualizer_app.seniority.use_cases.GetCurrentSeniorityListReport._get_most_recent_record"
        ) as mock_record_error:

            mock_record_error.side_effect = ValueError("no records in repository")

            uc.GetCurrentSeniorityListReport._get_most_recent_record = mock_record_error

            req = uc.requests.SeniorityReportRequest(use_current=True)

            res = uc.GetCurrentSeniorityListReport(mock_repo, mock_df_factory).execute(
                req
            )

            assert res.value["type"] == res.SYSTEM_ERROR
            assert res.value["message"] == "ValueError: no records in repository"

    @pytest.mark.parametrize(
        "inp_dict, exp_attrs",
        [({}, {"use_current": True}), ({"use_current": True}, {"use_current": True})],
    )
    def test_request(self, inp_dict, exp_attrs):

        request = uc.requests.SeniorityReportRequest.from_dict(inp_dict)

        assert bool(request)
        assert all(getattr(request, attr) == val for attr, val in exp_attrs.items())

    def test_request_failure(self):

        req_dict = dict(use_current=5)

        request = uc.requests.SeniorityReportRequest.from_dict(req_dict)

        assert isinstance(request, uc.requests.InvalidRequestObject)
        assert bool(request) is False
        assert request.has_errors()
        assert {
            "parameter": "use_current",
            "message": "'use_current' must be a boolean value",
        } in request.errors
