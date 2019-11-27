from datetime import datetime, date
from typing import Optional, Iterator, Tuple, Union
from dateutil.relativedelta import relativedelta
import logging

from .models import SeniorityList, Pilot

logger = logging.getLogger(__name__)


def calculate_seniority_list_span(sen_list: SeniorityList):
    """Return the earliest hire date and latest retire date from a SeniorityList"""
    min_hire_date = None
    max_retire_date = None

    for p in sen_list.pilot_data:
        if not min_hire_date or p.hire_date < min_hire_date:
            min_hire_date = p.hire_date
        if not max_retire_date or p.retire_date > max_retire_date:
            max_retire_date = p.retire_date

    return min_hire_date, max_retire_date


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

    min_hire, max_retire = calculate_seniority_list_span(sen_list)

    if isinstance(start, datetime):
        explicit_start = start.date()
    elif start is None:
        explicit_start = min_hire
    else:
        explicit_start = start

    if isinstance(end, datetime):
        explicit_end = end.date()
    elif end is None:
        explicit_end = max_retire
    else:
        explicit_end = end

    if not explicit_start < explicit_end:
        raise ValueError("somehow start >= end")

    target_pilot = pilot

    if pilot not in sen_list.pilot_data:
        raise ValueError(f"{pilot} not in {sen_list}")

    starting_pilots = sorted(sen_list.pilot_data)

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
