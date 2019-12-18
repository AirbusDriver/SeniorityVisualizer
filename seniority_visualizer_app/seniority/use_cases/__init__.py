import typing as t
import datetime as dt

import pandas as pd

from seniority_visualizer_app.shared.response_object import (
    ResponseFailure,
    ResponseSuccess,
)
from seniority_visualizer_app.shared.request_object import (
    ValidRequestObject,
    InvalidRequestObject,
)
from seniority_visualizer_app.shared.use_case import UseCase
from seniority_visualizer_app.shared.response_object import ResponseSuccess

from seniority_visualizer_app.seniority.entities import CsvRecord
from seniority_visualizer_app.seniority.exceptions import UseCaseError
from seniority_visualizer_app.seniority.dataframe import STANDARD_FIELDS

from ..repo import ICsvRepo
from .. import data_objects as do
from . import requests as uc_req

FIELDS = STANDARD_FIELDS


class FilterSeniorityLists:
    """
    Filter SeniorityRecords
    """

    pass


class GetCurrentSeniorityCsv(UseCase):
    """
    Retrieve the most recent seniority csv.
    """

    def __init__(self, repo: ICsvRepo):
        self.repo = repo

    def process_request(
        self, request: uc_req.SeniortyFilterRequest
    ) -> t.Union[ResponseSuccess, ResponseFailure]:
        records = self.repo.get_all()

        sorted_records = sorted(records, key=lambda r: r.published, reverse=False)

        if request.most_recent and records:
            return ResponseSuccess(sorted_records[-1])

        if request.most_recent and not records:
            return ResponseFailure.build_resource_error("no records in repo")

        if not request.most_recent and records:
            return ResponseSuccess(list(sorted_records))

        return ResponseSuccess(sorted_records)


class GetCurrentSeniorityListReport(UseCase):
    """
    Generate a SeniorityListStatistics report
    """

    def __init__(
        self, repo: ICsvRepo, df_factory: t.Callable[[CsvRecord], pd.DataFrame]
    ):
        self.repo = repo
        self.df_factory = df_factory

    def process_request(
        self, request: t.Union[ValidRequestObject, InvalidRequestObject]
    ):
        """
        Return a SeniorityListStatistics report from the most recent record
        in the repo.
        """

        resp = self._get_most_recent_record()

        if not resp:
            return resp
        else:
            record = resp.value

        df = self._make_df_from_record(record)

        report = self._make_report_from_df(df, valid_date=record.published)

        return ResponseSuccess(report)

    def _get_most_recent_record(self) -> t.Union[ResponseFailure, ResponseSuccess]:
        req = uc_req.SeniortyFilterRequest.from_dict(dict(most_recent=True))
        return GetCurrentSeniorityCsv(self.repo).execute(req)

    def _make_df_from_record(self, record: CsvRecord) -> pd.DataFrame:
        try:
            return self.df_factory(record)
        except Exception as e:
            raise UseCaseError(e, self)

    def _make_report_from_df(
        self, df: pd.DataFrame, valid_date: t.Optional[dt.datetime] = None
    ) -> do.SeniorityListStatistics:
        data = {
            "total_pilots": df[FIELDS.SENIORITY_NUMBER].count(),
            "valid_date": valid_date or None,
            "most_recent_class": valid_date or None,
            "total_retired": df[df[FIELDS.RETIRE_DATE] <= dt.datetime.now()].index.size,
            "span": do.SeniorityListSpan(valid_date, df[FIELDS.RETIRE_DATE].max()),
        }

        return do.SeniorityListStatistics(**data)
