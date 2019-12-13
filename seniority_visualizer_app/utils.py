# -*- coding: utf-8 -*-
"""Helper utilities and decorators."""
from datetime import datetime, date, timedelta
import re
from typing import Union, TypeVar

from flask import flash


DateCastable = TypeVar("DateCastable", datetime, date, str)


def flash_errors(form, category="warning"):
    """Flash all errors for a form."""
    for field, errors in form.errors.items():
        for error in errors:
            flash("{0} - {1}".format(getattr(form, field).label.text, error), category)


iso_regex = re.compile(
    r"""
    ^(?P<year>\d{4})
          (?P<ISOSEPARATOR>[-\s|/])
    (?P<month>\d{1,2})
          (?P=ISOSEPARATOR)
    (?P<day>\d{1,2})

    (?P<time>
          (?P<time_separator>[T\s])
    (?P<hour>\d{1,2})
    :
    (?P<minute>\d{1,2})
    :?
    (?P<second>\d{1,2})?
    [:.]?
    (?P<millisecond>\d{1,6})?
    )?
    $
    """,
    re.VERBOSE,
)


def to_iso(date_string: str) -> str:
    """
    Return an iso formatted string from a mostly iso string

    .. code-block::

        >>> to_iso("2020/1/1")
        '2020-01-01'
        >>> to_iso("2020-01-02 10:20:50")
        '2020-01-02T10:20:50'

    :raise ValueError: if string not a valid iso string
    """
    match = iso_regex.match(date_string)
    if not match:
        raise ValueError(f"Invalid isoformat string: {date_string}")
    gd = match.groupdict()

    time_string = gd.get("time") or ""
    if time_string and gd.get("time_separator") != "T":
        time_string = time_string.replace(gd["time_separator"], "T", 1)

    subbed = f"{gd['year']}-{gd['month'].zfill(2)}-{gd['day'].zfill(2)}{time_string}"
    return subbed


def cast_date(d: DateCastable) -> date:
    """
    Cast a date-like object into a datetime.date instance.

    .. code-block::

        >>> from datetime import date, datetime
        >>> cast_date(date(2020, 1, 5))
        datetime.date(2020, 1, 5)
        >>> cast_date(datetime(2020, 1, 5, 10, 20))
        datetime.date(2020, 1, 5)
        >>> cast_date("2020-1-5T10:20")
        datetime.date(2020, 1, 5)


    Accepts date, datetime, and 'YYYY-MM-DD[Thh:mm:ss.nnnnnn]'
    """
    if isinstance(d, datetime):
        return d.date()
    if isinstance(d, date):
        return d
    if isinstance(d, str):
        date_string = to_iso(d)
        return datetime.fromisoformat(date_string).date()

    raise TypeError("d must be a date, datetime, or an iso formatted string")
