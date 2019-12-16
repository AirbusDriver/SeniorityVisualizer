from __future__ import annotations
from typing import (
    Union,
    List,
    TypeVar,
    Dict,
    Callable,
    Generic,
    TYPE_CHECKING,
    Optional,
    Any,
    IO,
)
from pathlib import Path
import abc

import tablib

from seniority_visualizer_app.seniority.entities import Pilot, SeniorityList
from seniority_visualizer_app.utils import cast_date
from .exceptions import LoaderError


T = TypeVar("T")


PILOT_CASTING = {
    "hire_date": lambda s: cast_date(s),
    "retire_date": lambda s: cast_date(s),
    "employee_id": lambda s: s,
    "literal_seniority_number": lambda s: int(s),
}

SENIORITY_LIST_CASTING = {"published_date": lambda s: cast_date(s)}


class SeniorityListLoader:
    def __init__(self, headers: Dict[str, str] = None):
        self.headers = headers or {}

    def _load_stream_to_dicts(self, stream: IO) -> List[dict]:
        """Load just about any tabular datafile into dicts"""
        data = stream.read()

        dataset = tablib.Dataset()

        dataset.load(data)

        return dataset.dict

    @staticmethod
    def rename_keys(d: dict, headers: dict) -> dict:
        """
        Return a dict with the values from headers overriding the key names

        Example:

            source:

                col1 | col2 | col3
                ==================
                dat1 | dat2 | dat3

            headers:

                {
                   col2: desired
                }

            output:

                col1 | desired | col3
                =====================
                dat1 |   dat2  | dat3
        """
        out = {}
        for key, val in d.items():
            out[headers.get(key, key)] = val

        return out

    def load_from_stream(self, stream: IO, **kwargs) -> SeniorityList:
        """
        Create a SeniorityList object from a stream-like object. Additional
        kwargs are passed to the `SeniorityList.__init__()` method.
        """
        data = self._load_stream_to_dicts(stream)

        header_swapped = (self.rename_keys(d, self.headers) for d in data)

        pilots = (Pilot.from_dict(d) for d in header_swapped)

        try:
            return SeniorityList(pilots=pilots, **kwargs)
        except KeyError as e:
            s = (
                f"Could not create pilot object without key: {e}. "
                f"Make sure the loader has appropriate headers.\n"
                f"Headers: {self.headers}\n"
                f"Raw Data Keys: {list(data[0].keys())}"
            )
            raise LoaderError(s)
