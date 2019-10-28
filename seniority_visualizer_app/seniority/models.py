"""
Contains the models for the management of seniority data.
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, Iterable, Iterator, Optional, Union, List

from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method

from .utils import standardize_employee_id
from seniority_visualizer_app.database import (
    Column,
    Model,
    SurrogatePK,
    db,
    relationship,
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

    def to_seniority_list(self) -> SeniorityList:
        """
        Return a `SeniorityList` from the `SeniorityListRecord` object.
        """
        pilots = []
        for pr in self.pilots:
            pilots.append(pr.to_pilot())

        sen_list = SeniorityList(pilots)

        return sen_list


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

    @hybrid_property
    def standardized_employee_id(self):
        """A standardized version of the employee_id attribute"""
        return standardize_employee_id(self.employee_id)

    def to_pilot(self) -> Pilot:
        """Return a Pilot object from PilotRecord"""
        return Pilot.from_dict(self.to_dict())

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

    def to_dict(self):
        """
        Return a dict of pilot record information
        """
        dict_keys = [
            "employee_id",
            "seniority_list_id",
            "hire_date",
            "retire_date",
            "literal_seniority_number",
            "first_name",
            "last_name",
            "base",
            "seat",
            "aircraft",
        ]
        return {k: getattr(self, k, None) for k in dict_keys}


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
        self._hire_date = hire_date
        self._retire_date = retire_date
        self.literal_seniority_number = literal_seniority_number

        if not (
            isinstance(hire_date, (date, datetime))
            and isinstance(retire_date, (date, datetime))
        ):
            raise TypeError(
                "'hire_date' and 'retire_date' must be of type date or datetime"
            )

    @property
    def hire_date(self) -> date:
        if isinstance(self._hire_date, datetime):
            return self._hire_date.date()
        return self._hire_date

    @hire_date.setter
    def hire_date(self, val: Union[date, datetime]) -> None:
        if not isinstance(val, (date, datetime)):
            raise TypeError("val must be date or datetime")
        self._hire_date = val

    @property
    def retire_date(self) -> date:
        if isinstance(self._retire_date, datetime):
            return self._retire_date.date()
        return self._retire_date

    @retire_date.setter
    def retire_date(self, val: Union[date, datetime]) -> None:
        if not isinstance(val, (date, datetime)):
            raise TypeError("val must be date or datetime")
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

    @classmethod
    def from_dict(cls, _dict: Dict[str, Any]) -> Pilot:
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

    def is_active_on(self, ref_date: Union[date, datetime, None] = None) -> bool:
        """
        Return True if the pilot is active on `ref_date`. If a `ref_date` is not given,
        the system current date will be used. The pilot is considered "active" if
        `Pilot.hire_date` <= `ref_date` < `Pilot.retire_date`.

        :param ref_date: date to reference, date.today() will be used if None
        :return: True if pilot active on `ref_date`
        """
        if ref_date is None:
            _date = date.today()
        elif isinstance(ref_date, datetime):
            _date = ref_date.date()
        else:
            _date = ref_date
        if not isinstance(_date, date):
            raise TypeError("ref_date must be of type date or datetime or None")

        return self.hire_date <= _date < self.retire_date


class SeniorityList:
    """
    Models collection and hierarchical behaviors of individual Pilot records
    """

    def __init__(self, pilots: Optional[Iterable[Pilot]] = None):
        self._pilots = [] if pilots is None else [p for p in pilots]

    def __repr__(self):
        s = f"<{type(self).__name__}(len: {len(self)})>"
        return s

    def __len__(self):
        return len(self._pilots)

    @property
    def pilot_data(self):
        """All pilots"""
        return self._pilots.copy()

    @pilot_data.setter
    def pilot_data(self, val):
        raise AttributeError("pilot data is read only")

    def filter_active_on(
        self, ref_date: Union[date, datetime, None] = None
    ) -> Iterator[Pilot]:
        """
        Return an iterator of Pilot objects that are active on `ref_date`. If it is
        not provided, the system date.today() is used.

        :param ref_date: date to check pilot status against
        :return: iterator of Pilot objects
        """
        ref = date.today() if ref_date is None else ref_date
        if isinstance(ref, datetime):
            ref = ref.date()
        return (p for p in self._pilots if p.is_active_on(ref))
