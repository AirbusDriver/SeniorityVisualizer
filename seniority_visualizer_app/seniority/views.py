from typing import List, Union


from flask import Blueprint, make_response, render_template
from flask_login import login_required, current_user

from .models import PilotRecord
from .utils import standardize_employee_id

from seniority_visualizer_app.user.models import Permissions
from ..shared.entities import EmployeeID

blueprint = Blueprint(
    "seniority", __name__, url_prefix="/seniority", static_folder="../static"
)


@blueprint.before_request
@login_required
def verify_user_has_seniority_permissions():
    """
    Return error page for insufficient permissions
    """
    if not current_user.role.has_permission(Permissions.VIEW_SENIORITY_DATA):
        return make_response(
            "You do not have permission to view seniority data until you confirm your company email.",
            401,
        )


def get_pilot_records_for_employee_id(
    employee_id: Union[str, int, EmployeeID]
) -> List[PilotRecord]:
    """Return a list of pilot records from an employee id"""
    _id = standardize_employee_id(employee_id)

    initial = PilotRecord.query.filter(
        PilotRecord.employee_id.ilike(f"%{employee_id}%")
    ).all()
    return [record for record in initial if record.standardized_employee_id == _id]


# only in this commit for the blueprint hook test
@blueprint.route("status")
def current_status():
    """
    Present the user with current seniority list information.
    """

    return ""
