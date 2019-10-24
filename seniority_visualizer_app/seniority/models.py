"""
Contains the models for the management of seniority data.
"""
from __future__ import annotations
from typing import Union, Optional, List, Dict, Iterable, Callable
from datetime import datetime, date, timedelta
from pathlib import Path
import csv

from seniority_visualizer_app.database import (
    Model,
    Column,
    relationship,
    SurrogatePK,
    db,
)


class SeniorityListRecord(Model, SurrogatePK):
    """
    Collection of PilotRecords.
    """

    __tablename__ = "seniority_list_records"

    published_date = db.Column(db.DateTime)
    added_date = db.Column(db.DateTime, default=datetime.utcnow)
    company_name = db.Column(db.String(32))

    def __init__(self, published_date: datetime, **kwargs):
        super().__init__(published_date=published_date, **kwargs)


class PilotRecord(Model, SurrogatePK):
    """
    Record store of information from a single pilot on a published seniority list.
    """

    __tablename__ = "pilot_records"

    employee_id = Column(db.String(16), nullable=False)
    seniority_list_id = Column(db.ForeignKey("seniority_list_records.id"))
    seniority_list = relationship("SeniorityListRecord", backref="pilots")
    hire_date = Column(db.DateTime)
    retire_date = Column(db.DateTime)
    literal_seniority_number = Column(db.Integer)
    first_name = Column(db.String(64))
    last_name = Column(db.String(64))
    base = Column(db.String(8))
    seat = Column(db.String(8))
    aircraft = Column(db.String(8))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        s = f"<{type(self).__name__} - emp_id: {self.employee_id}>"
        return s

    # branch: implement and test
    def to_pilot(self):
        return Pilot.from_pilot_record(self)

    @classmethod
    def from_dict(cls, _dict: Dict) -> PilotRecord:
        out = _dict.copy()
        out["employee_id"] = str(out["employee_id"])
        out["literal_seniority_number"] = int(out["literal_seniority_number"])
        if not (
            isinstance(out["hire_date"], (date, datetime))
            and isinstance(out["retire_date"], (date, datetime))
        ):
            raise TypeError(
                "hire_date and retire_date must be instances of date or datetime"
            )

        return cls(**out)


# branch: implement
class Pilot:
    """
    Models the individual pilot record interactions and states
    """

    def __init__(
        self,
        employee_id: str,
        hire_date: Union[date, datetime],
        retire_date: Union[date, datetime],
        literal_seniority_number: Optional[int] = None,
    ):
        self.employee_id = employee_id
        self._hire_date = hire_date if isinstance(hire_date, date) else hire_date.date()
        self._retire_date = (
            retire_date if isinstance(retire_date, date) else retire_date.date()
        )
        self.literal_seniority_number = literal_seniority_number

        if not (
            isinstance(hire_date, (date, datetime))
            and isinstance(retire_date, (date, datetime))
        ):
            raise TypeError(
                "'hire_date' and 'retire_date' must be of type date or datetime"
            )

    @classmethod
    def from_pilot_record(cls, pilot_record: PilotRecord) -> Pilot:
        pass

    @property
    def hire_date(self) -> date:
        return self._hire_date

    @hire_date.setter
    def hire_date(self, val: Union[date, datetime]) -> None:
        if isinstance(val, datetime):
            val = val.date()
        self._hire_date = val

    @property
    def retire_date(self) -> date:
        return self._retire_date

    @retire_date.setter
    def retire_date(self, val: Union[date, datetime]) -> None:
        if isinstance(val, datetime):
            val = val.date()
        self._retire_date = val

    def __lt__(self, other):
        """Returns True if self.is_senior_to(other)"""
        return self.is_senior_to(other)

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __hash__(self):
        return id(self)

    def __repr__(self):
        s = f"<{type(self).__name__}(emp_id: {self.employee_id} hired: {self.hire_date} retires: {self.retire_date})>"
        return s

    # todo: add strategies
    def is_senior_to(self, other: Pilot) -> bool:
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


# branch: implement
class SeniorityList:
    """
    Models collection and hierarchical behaviors of individual Pilot records
    """

    def __init__(self, pilots: Optional[Iterable[Pilot]] = None):
        self._pilots = [] if pilots is None else pilots[::]
