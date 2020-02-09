from typing import Optional, Iterator
import datetime as dt

from bokeh import plotting as plt
import pandas as pd

from dateutil.relativedelta import relativedelta as rel_del


from seniority_visualizer_app.utils import cast_date, DateCastable
from .utils import standardize_employee_id
from .entities import SeniorityList
from .statistics import calculate_seniority_list_span


# todo: remove this in favor of statistics version
def generate_date_indices(
    start: DateCastable, end: DateCastable, yield_overflow=False
) -> Iterator[dt.date]:
    """
    Yield a series of date objects from start to end (inclusive)
    """
    start_date = cast_date(start)
    end_date = cast_date(end)

    date_idx = start_date

    yield date_idx

    while True:
        date_idx += rel_del(months=1)
        if date_idx <= end_date:
            yield date_idx
            continue
        if yield_overflow:
            yield date_idx
            break
        break


