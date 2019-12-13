from __future__ import annotations
from datetime import date, datetime
from typing import Union, Optional, Dict, Any, Iterable, Iterator, List

import pandas as pd

from seniority_visualizer_app.utils import cast_date, DateCastable
from .exceptions import SeniorityListError


# todo: sub in new employee_id entity
class Pilot:
    """
    Models the individual pilot record interactions and states
    """

    def __init__(
        self,
        employee_id: str,
        hire_date: DateCastable,
        retire_date: DateCastable,
        literal_seniority_number: Optional[int] = None,
    ):
        self.employee_id: str = employee_id
        self.hire_date = hire_date  # type: ignore
        self.retire_date = retire_date  # type: ignore
        self.literal_seniority_number = literal_seniority_number

    @property
    def hire_date(self) -> date:
        return self._hire_date

    @hire_date.setter
    def hire_date(self, val: DateCastable) -> None:
        self._hire_date = cast_date(val)

    @property
    def retire_date(self) -> date:
        if isinstance(self._retire_date, datetime):
            return self._retire_date.date()
        return self._retire_date

    @retire_date.setter
    def retire_date(self, val: DateCastable) -> None:
        self._retire_date = cast_date(val)

    def __lt__(self, other):
        """Returns True if self.is_senior_to(other)"""
        return self.is_senior_to(other)

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __hash__(self):
        t = (self.employee_id, self.hire_date, self.retire_date)
        return hash(t)

    def __repr__(self):
        s = f"<{type(self).__name__}(emp_id: {self.employee_id} hired: {self.hire_date} retires: {self.retire_date})>"
        return s

    # fixme: seniority number mismatched key
    @classmethod
    def from_dict(cls, _dict: Dict[str, Any]) -> "Pilot":
        """
        Return a Pilot from a dict
        """
        required_kwargs = [
            "employee_id",
            "hire_date",
            "retire_date",
            "literal_seniority_number",
        ]
        init_dict = dict.fromkeys(required_kwargs)

        init_dict["employee_id"] = str(_dict["employee_id"])
        init_dict["hire_date"] = _dict["hire_date"]
        init_dict["retire_date"] = _dict["retire_date"]
        init_dict["literal_seniority_number"] = _dict["literal_seniority_number"]

        return cls(**init_dict)

    def to_dict(self):
        """
        Return a dict representation of pilot data.
        """
        return {
            "employee_id": self.employee_id,
            "hire_date": self.hire_date,
            "retire_date": self.retire_date,
            "seniority_number": self.literal_seniority_number,
        }

    # todo: add strategies
    def is_senior_to(self, other: "Pilot") -> bool:
        """
        Return True if senior to other

        Seniority determined by hire date > retire date (earlier retirements are considered senior) >
        literal seniority numbers (by value, or the one having one is considered more senior)

        :param other: other Pilot object
        :return: bool
        """
        if self.hire_date < other.hire_date:
            return True
        if self.hire_date == other.hire_date:
            if self.retire_date < other.retire_date:
                return True
            if self.retire_date == other.retire_date:
                self_lit = self.literal_seniority_number
                other_lit = other.literal_seniority_number
                if self_lit is not None and other_lit is not None:
                    return self_lit < other_lit
                else:
                    return self_lit is not None and other_lit is None
        return False

    def is_active_on(self, ref_date: Optional[DateCastable] = None) -> bool:
        """
        Return True if the pilot is active on `ref_date`. If a `ref_date` is not given,
        the system current date will be used. The pilot is considered "active" if
        `Pilot.hire_date` <= `ref_date` < `Pilot.retire_date`.

        :param ref_date: date to reference, date.today() will be used if None
        :return: True if pilot active on `ref_date`
        """
        if ref_date is None:
            _date = date.today()
        else:
            _date = cast_date(ref_date)

        return self.hire_date <= _date < self.retire_date


class SeniorityList:
    """
    Models collection and hierarchical behaviors of individual Pilot records
    """

    def __init__(
        self,
        pilots: Optional[Iterable[Pilot]] = None,
        published_date: Optional[DateCastable] = None,
    ):
        self._pilots: List[Pilot] = [] if pilots is None else [p for p in pilots]
        self.published_date: Optional[date] = published_date  # type: ignore

    def __repr__(self):
        s = f"<{type(self).__name__}(len: {len(self)})>"
        return s

    def __len__(self):
        return len(self._pilots)

    def __contains__(self, item):
        try:
            return self._get_pilot_index(item, self.pilot_data)
        except ValueError:
            return False

    @property
    def published_date(self) -> Optional[date]:
        return self._published_date

    @published_date.setter
    def published_date(self, new_date: Optional[DateCastable]):
        if new_date is None:
            self._published_date = None
            return
        self._published_date = cast_date(new_date)

    # todo: extract to serializer
    def to_df(self, df_kwargs: Optional[Dict[str, Any]] = None):
        """Return a Pandas Dataframe of pilot info"""
        df_kwargs = df_kwargs or {}
        df = pd.DataFrame([p.to_dict() for p in self._pilots], **df_kwargs)
        df.hire_date = pd.to_datetime(df.hire_date)
        df.retire_date = pd.to_datetime(df.retire_date)
        return df

    @property
    def pilot_data(self):
        """All pilots"""
        return self._pilots.copy()

    @pilot_data.setter
    def pilot_data(self, val):
        raise AttributeError("pilot data is read only")

    @property
    def sorted_pilot_data(self) -> List[Pilot]:
        """Presorted pilot data"""
        return sorted(self.pilot_data)

    @sorted_pilot_data.setter
    def sorted_pilot_data(self, val):
        raise AttributeError("sorted pilot data is read only")

    def filter_active_on(
        self, ref_date: Optional[DateCastable] = None
    ) -> Iterator[Pilot]:
        """
        Return an iterator of Pilot objects that are active on `ref_date`. If it is
        not provided, the system date.today() is used.

        :param ref_date: date to check pilot status against
        :return: iterator of Pilot objects
        """
        ref = date.today() if ref_date is None else cast_date(ref_date)

        return (p for p in self.sorted_pilot_data if p.is_active_on(ref))

    def lookup_pilot_seniority_number(
        self, pilot: Pilot, date_: Optional[DateCastable] = None
    ) -> int:
        """
        Return the seniority number of a pilot (1-indexed) within a seniority list. If the pilot is
        not present in the seniority list, raise SeniorityListError

        :raises SeniorityListError: pilot not a member of seniority list

        :param pilot: pilot to check
        :param date_: get seniority number as of date
        """
        if date_ is not None:
            casted = cast_date(date_)
            data = self.filter_active_on(casted)
        else:
            data = iter(self.sorted_pilot_data)

        try:
            idx = self._get_pilot_index(pilot, data)
            return idx + 1
        except ValueError:
            raise SeniorityListError(f"{pilot} not in {self}")

    @staticmethod
    def _get_pilot_index(pilot: Pilot, data: Iterable[Pilot]) -> int:
        """Get the index of a pilot in a list of pilot data"""
        return sorted(data).index(pilot)

    @classmethod
    def from_dict(cls, dict_: dict) -> SeniorityList:
        """Return a SeniorityList with from from the `SeniorityList.__init__()`"""
        pilots = [Pilot.from_dict(p) for p in dict_["pilots"]]

        return cls(pilots=pilots, published_date=dict_.get("published_date"))
