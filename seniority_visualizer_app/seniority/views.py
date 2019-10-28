from typing import List, Union

from flask import Blueprint


from .models import PilotRecord, SeniorityListRecord
from .utils import standardize_employee_id
from seniority_visualizer_app.user.models import User

blueprint = Blueprint(
    "seniority", __name__, url_prefix="/seniority", static_folder="../static"
)


def get_pilot_records_for_employee_id(employee_id: Union[str, int]) -> List[PilotRecord]:
    """Return a list of pilot records from user"""
    _id = standardize_employee_id(employee_id)

    initial = PilotRecord.query.filter(PilotRecord.employee_id.ilike(f"%{employee_id}%")).all()
    return [record for record in initial if record.standardized_employee_id == _id]
