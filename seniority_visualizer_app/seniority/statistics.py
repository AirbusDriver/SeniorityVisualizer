from datetime import datetime, date
from typing import Optional, Iterator, Tuple, Union
import typing as t
from dateutil.relativedelta import relativedelta
import logging

import pandas as pd
import numpy as np

from seniority_visualizer_app.seniority.entities import Pilot, SeniorityList
from . import data_objects as do
from .dataframe import STANDARD_FIELDS as FIELDS, require_fields
from .exceptions import CalculationError

logger = logging.getLogger(__name__)

DateLike = t.Union[date, pd.Timestamp]
DateSeries = t.Union[t.Iterable[DateLike], pd.DatetimeIndex]


def calculate_seniority_list_span(sen_list: SeniorityList) -> do.SeniorityListSpan:
    """Return the earliest hire date and latest retire date from a SeniorityList"""
    min_hire_date = None
    max_retire_date = None

    for p in sen_list.pilot_data:
        if not min_hire_date or p.hire_date < min_hire_date:
            min_hire_date = p.hire_date
        if not max_retire_date or p.retire_date > max_retire_date:
            max_retire_date = p.retire_date

    if not (min_hire_date is not None and max_retire_date is not None):
        raise CalculationError(f"no min/max could be deterived from {sen_list}")

    return do.SeniorityListSpan(
        earliest_hire=min_hire_date, latest_retire=max_retire_date
    )


def iter_seniority_over_time(
    sen_list: SeniorityList,
    pilot: Pilot,
    start: Optional[Union[datetime, date]] = None,
    end: Optional[Union[datetime, date]] = None,
    delta: relativedelta = relativedelta(months=3),
) -> Iterator[Tuple[date, Optional[int], int]]:
    """
    Yield Tuple[datetime, seniority_number, total_active] for a given pilot over a time series.

    :param sen_list: SeniorityList instance to run calculation over
    :param pilot: Pilot object to yield seniority information about
    :param start: first date to yield data for [default: earliest hire date]
    :param end: last date to yield data for [default: latest retirement date]
    :param delta: interval expressed as a :py:func:`relativedelta`
    """

    span = calculate_seniority_list_span(sen_list)

    if isinstance(start, datetime):
        explicit_start = start.date()
    elif start is None:
        explicit_start = span.earliest_hire
    else:
        explicit_start = start

    if isinstance(end, datetime):
        explicit_end = end.date()
    elif end is None:
        explicit_end = span.latest_retire
    else:
        explicit_end = end

    if not explicit_start < explicit_end:
        raise ValueError("somehow start >= end")

    starting_pilots = sorted(sen_list.pilot_data)

    for p in starting_pilots:
        if p.employee_id == pilot.employee_id:
            target_pilot = p
            break
    else:
        raise ValueError(f"{pilot} not in {sen_list}")

    date_index = explicit_start
    stop = explicit_end

    current_pilots = starting_pilots

    while date_index <= stop:
        try:
            current_seniority_number: Optional[int] = current_pilots.index(
                target_pilot
            ) + 1
        except ValueError:
            current_seniority_number = None

        yield date_index, current_seniority_number, len(current_pilots)

        date_index += delta

        current_pilots = [p for p in starting_pilots if p.is_active_on(date_index)]


def calculate_pilot_seniority_statistics(
    pilot: Pilot, seniority_list: SeniorityList
) -> do.PilotSeniorityStatistics:
    """Return a `PilotSeniorityStatistics` data object"""

    seniority = seniority_list.lookup_pilot_seniority_number(pilot)

    statistics = do.PilotSeniorityStatistics(
        current_seniority_number=seniority,
        hire_date=pilot.hire_date,
        retire_date=pilot.retire_date,
        employee_id=pilot.employee_id,
    )

    return statistics


def make_seniority_plot_date_index(
    df: pd.DataFrame, start=None, end=None, freq="M", pin_to_first=True
) -> pd.DatetimeIndex:
    if FIELDS.RETIRE_DATE not in df:
        raise ValueError(f"df missing {FIELDS.RETIRE_DATE} column")

    first_date = start if start is not None else date.today()

    last_date = df[FIELDS.RETIRE_DATE].max() if end is None else end

    if pin_to_first:
        first_date = pin_to_first_day(first_date)
        last_date = ffwd_and_pin(last_date)

    dates = pd.date_range(start=first_date, end=last_date, freq="D")

    day_filter = {
        "D": lambda d: True,
        "M": lambda d: d.day == min(first_date.day, 28),
    }.get(freq, "M")

    return dates[dates.map(day_filter)]


def make_pilots_remaining_series(
    df: pd.DataFrame, index: pd.DatetimeIndex, name: str = "retirements"
) -> pd.Series:
    out = []

    retire_dates = df[FIELDS.RETIRE_DATE]

    for date_ in index:
        active = retire_dates[retire_dates > date_]

        out.append(active.size)

    return pd.Series(data=out, index=index, dtype=int, name=name)


def pin_to_first_day(
    timestamp: t.Union[pd.Timestamp, date, datetime], combine_time: bool = False
) -> datetime:
    year = timestamp.year
    month = timestamp.month
    day = 1

    out = pd.Timestamp(year=year, month=month, day=day)

    if combine_time:
        if not hasattr(timestamp, "time"):
            time = pd.Timestamp.today()
        else:
            time = timestamp.time()  # type: ignore

        return pd.Timestamp.combine(out, time)
    return out.to_pydatetime()


def ffwd_and_pin(timestamp: t.Union[date, datetime, pd.Timestamp]) -> datetime:
    cur = timestamp

    while cur.day != 1 and cur.month == timestamp.month:
        cur = cur + pd.Timedelta(days=7)

    return pin_to_first_day(cur, combine_time=True)


def calculate_retirements_over_time(
    ds: pd.Series, interval_series: pd.IntervalIndex
) -> t.List[int]:
    """Return a list of the number of retirements that occur within each Interval"""

    data = ds.groupby(pd.cut(ds, interval_series)).count()

    return list(data)


@require_fields(FIELDS.RETIRE_DATE, FIELDS.SENIORITY_NUMBER, FIELDS.EMPLOYEE_ID)
def calculate_number_of_active_senior_pilots_for_dates(
    df: pd.DataFrame, date_series: DateSeries, employee_id: str
) -> t.List[float]:
    """
    Return a list of floats (or NaN) representing the number of pilots who would be active and senior
    to the pilot represented by the `employee_id`. `float("nan")` is returned for dates in which the pilot
    retire date >= date.

    :param df: dataframe containing seniority information. Must contain the standard SENIORITY_NUMBER, EMPLOYEE_ID,
    and RETIRE_DATE fields.
    :param date_series: dates to perform operations on
    :param employee_id: employee_id as found in dataframe

    :raise ValueError: if record does not exist for `employee_id`
    """

    def senior_filter(sen_num: int, ref_date: str):
        def _senior(ds: pd.Series):
            return ds[
                (ds[F.SENIORITY_NUMBER] < sen_num) & (df[F.RETIRE_DATE] > ref_date)
            ]

        return _senior

    F = FIELDS

    target_info = df[df[F.EMPLOYEE_ID] == employee_id]

    if target_info.shape[0] == 0:
        raise ValueError(f"no record with {F.EMPLOYEE_ID} == {employee_id}")

    target_record = target_info.iloc[0]

    target_sen_num = target_record[F.SENIORITY_NUMBER]

    data = pd.DataFrame(index=date_series)

    data["seniority_on_date"] = data.index.map(
        lambda d: senior_filter(target_sen_num, d)(df).shape[0]
    )

    data[data.index > target_record[F.RETIRE_DATE]] = float("nan")

    return data["seniority_on_date"].to_list()
