"""
Contains the models for the management of seniority data.
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Dict
from collections import OrderedDict

from sqlalchemy.ext.hybrid import hybrid_property
import pandas as pd

from seniority_visualizer_app.seniority.entities import Pilot, SeniorityList
from .utils import standardize_employee_id
from seniority_visualizer_app.database import (
    Column,
    Model,
    SurrogatePK,
    db,
    relationship,
)

# todo: change datetime to date
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

    def to_df(self, **kwargs) -> pd.DataFrame:
        """
        Return a DataFrame from the SeniorityListRecord

        :param kwargs: see :func:`pd.DataFrame.__init__()` **kwargs
        :return: DataFrame from pilot records
        """
        df = pd.DataFrame((p.to_dict() for p in self.pilots), **kwargs)
        return df

    def to_dict(self):
        """
        Return a list of dicts of each PilotRecord in object
        """
        return [p.to_dict() for p in self.pilots]

    # todo: implement
    @classmethod
    def from_entity(cls, entity: SeniorityList) -> SeniorityListRecord:
        pilots = (PilotRecord.from_entity(pilot) for pilot in entity.pilot_data)

        if entity.published_date is None:
            use_date: date = date.today()
        else:
            use_date: date = entity.published_date

        published_date = entity.published_date or datetime.now()

        out = SeniorityListRecord(published_date=use_date)

        for p in pilots:
            p.seniority_list = out

        return out


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

    def to_dict(self) -> OrderedDict:
        """
        Return an OrderedDict of pilot record information
        """
        dict_keys = [
            "employee_id",
            "literal_seniority_number",
            "seniority_list_id",
            "hire_date",
            "retire_date",
            "first_name",
            "last_name",
            "base",
            "seat",
            "aircraft",
        ]
        out = OrderedDict({k: getattr(self, k, None) for k in dict_keys})
        out["employee_id"] = standardize_employee_id(self.employee_id)
        return out

    @classmethod
    def from_entity(cls, obj: Pilot) -> PilotRecord:
        out = PilotRecord(
            employee_id=str(obj.employee_id),
            hire_date=obj.hire_date,
            retire_date=obj.retire_date,
        )
        return out
