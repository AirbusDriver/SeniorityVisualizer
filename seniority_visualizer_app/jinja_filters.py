"""Filters for Jinja templating environment"""
import typing as t
import datetime as dt


def format_datetime(value: t.Union[dt.date], format="iso") -> str:
    """Return a formatted string from a date-like object"""

    if format == "iso":
        return value.isoformat()
    else:
        selected = {"date": "%m %b, %Y"}.get(format)

        return value.strftime(selected) if selected is not None else value.isoformat()
