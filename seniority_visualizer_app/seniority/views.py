from typing import List, Union
from pathlib import Path
import uuid
import io

import pandas as pd

from flask import Blueprint, make_response, render_template, g, current_app, Flask
from flask_login import login_required, current_user

from .models import PilotRecord
from .utils import standardize_employee_id

from seniority_visualizer_app.user.models import Permissions
from .repo import CsvRepoInMemory, ICsvRepo
from .entities import CsvRecord
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


def get_repo(app: Flask) -> ICsvRepo:
    """
    Return the current repository with loaded CsvRecords.

    """

    repo_file = app.config["CURRENT_SENIORITY_LIST_CSV"]

    published = app.config["CURRENT_SENIORITY_LIST_PUBLISHED"]
    if repo_file is None:
        raise ValueError("CURRENT_SENIORITY_LIST_CSV config not set")

    fp = Path(repo_file).resolve()

    if not fp.exists():
        raise FileNotFoundError(f"{fp} does not exist")

    repo: ICsvRepo = CsvRepoInMemory()

    record = CsvRecord(uuid.uuid4(), published, fp.read_text())

    repo.save(record)

    return repo


def make_df_from_record(record: CsvRecord) -> pd.DataFrame:
    """Return a pd.DataFrame from a CsvRecord."""
    buffer = io.StringIO()
    buffer.write(record.text)
    buffer.seek(0)

    return pd.read_csv(buffer, parse_dates=["retire_date"])


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
