"""
Contains the models for the management of seniority data.
"""
from datetime import date, datetime
from typing import Dict, Optional

from sqlalchemy.ext.hybrid import hybrid_property

from seniority_visualizer_app.database import (
    Column,
    Model,
    SurrogatePK,
    db,
    relationship,
)
from seniority_visualizer_app.utils import cast_date, DateCastable
from .entities import Pilot, SeniorityList
from .utils import standardize_employee_id


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

    def to_entity(self) -> SeniorityList:
        """
        Return a `SeniorityList` from the `SeniorityListRecord` object.
        """
        pilots = []
        for pr in self.pilots:
            pilots.append(pr.to_entity())

        sen_list = SeniorityList(pilots)

        return sen_list

    @classmethod
    def from_entity(
        cls, entity: SeniorityList, published_date: Optional[DateCastable] = None
    ) -> SeniorityListRecord:
        pilots = (PilotRecord.from_entity(pilot) for pilot in entity.pilot_data)

        if published_date is not None:
            casted: datetime = datetime.fromordinal(
                cast_date(published_date).toordinal()
            )
        else:
            casted = datetime.now()

        out = SeniorityListRecord(published_date=casted)

        if casted:
            out.published_date = casted

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

    def to_entity(self) -> Pilot:
        """Return a Pilot object from PilotRecord"""
        return Pilot(
            employee_id=self.standardized_employee_id,
            hire_date=self.hire_date,
            retire_date=self.retire_date,
            literal_seniority_number=self.literal_seniority_number,
        )

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

    @classmethod
    def from_entity(cls, obj: Pilot) -> PilotRecord:
        out = PilotRecord(
            employee_id=str(obj.employee_id),
            hire_date=obj.hire_date,
            retire_date=obj.retire_date,
            literal_seniority_number=obj.literal_seniority_number,
        )
        return out
