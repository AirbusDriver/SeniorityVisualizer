from typing import List, Union
from pathlib import Path
import uuid
from hashlib import md5
import io
import json
import datetime as dt

import pandas as pd
from flask import (
    Blueprint,
    make_response,
    render_template,
    g,
    current_app,
    Flask,
    flash,
    jsonify,
    request,
)
from flask_login import login_required, current_user

from ..extensions import cache

from .models import PilotRecord
from .utils import standardize_employee_id
from seniority_visualizer_app.user.models import Permissions
from .repo import CsvRepoInMemory, ICsvRepo
from .entities import CsvRecord
from .use_cases import GetCurrentSeniorityCsv
from . import statistics as stat
from .dataframe import STANDARD_FIELDS, make_standardized_seniority_dataframe
from .data_objects import SeniorityListStatistics
from ..shared.entities import EmployeeID
from .use_cases import GetCurrentSeniorityCsv, GetCurrentSeniorityListReport
from . import use_cases as uc

blueprint = Blueprint(
    "seniority", __name__, url_prefix="/seniority", static_folder="../static"
)


@blueprint.before_request
@login_required
def verify_user_has_seniority_permissions():
    """
    Return error page for insufficient permissions
    """
    if current_user.role.has_permission(Permissions.ADMIN):
        return
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

    df = pd.read_csv(buffer, parse_dates=["retire_date"])

    fields = {
        "seniority_number": STANDARD_FIELDS.SENIORITY_NUMBER,
        "cmid": STANDARD_FIELDS.EMPLOYEE_ID,
        "base": STANDARD_FIELDS.BASE,
        "seat": STANDARD_FIELDS.SEAT,
        "retire_date": STANDARD_FIELDS.RETIRE_DATE,
        "fleet": STANDARD_FIELDS.FLEET,
    }

    return make_standardized_seniority_dataframe(df, fields=fields)


def get_pilot_records_for_employee_id(
    employee_id: Union[str, int, EmployeeID]
) -> List[PilotRecord]:
    """Return a list of pilot records from an employee id"""
    _id = standardize_employee_id(employee_id)

    initial = PilotRecord.query.filter(
        PilotRecord.employee_id.ilike(f"%{employee_id}%")
    ).all()
    return [record for record in initial if record.standardized_employee_id == _id]


@blueprint.route("status")
@blueprint.route("/")
def current_status():
    """
    Present the user with current seniority list information.
    """

    repo = get_repo(current_app)
    res = GetCurrentSeniorityListReport(repo, make_df_from_record).execute(
        uc.requests.SeniorityReportRequest()
    )
    if not res:
        current_app.logger.error(res.value)
        return render_template(
            "seniority/current_status.html", error='No records currently found'
        )
    else:
        response = render_template(
            "seniority/current_status.html", report=res.value, error=None
        )
        return response


@blueprint.route("retirements")
def plot_retirements():
    """
    Present the base plot template
    """
    from bokeh.resources import CDN
    from bokeh.plotting import figure, ColumnDataSource
    from bokeh.embed import components
    from bokeh.models import HoverTool

    repo = get_repo(current_app)

    try:
        record = GetCurrentSeniorityCsv(repo).execute()
    except ValueError:
        flash("No records in repository")
        return render_template("seniority/base_plot.html", errors=True)

    fig = figure(title="Remaining Pilots", x_axis_type="datetime")

    df = make_df_from_record(record)

    dates = stat.make_seniority_plot_date_index(
        df, end=df[STANDARD_FIELDS.RETIRE_DATE].max(), freq="M"
    )

    source_df = pd.DataFrame(
        index=dates,
        data=stat.make_pilots_remaining_series(df, dates),
        columns=["retirements"],
    )
    source_df.index.name = "date"

    source = ColumnDataSource(source_df)

    fig.line(x="date", y="retirements", source=source)

    hov = HoverTool(
        mode="vline",
        tooltips=[("Date", "@date{%F}"), ("Active", "@retirements")],
        formatters={"date": "datetime"},
    )
    repo = get_repo(current_app)

    record = GetCurrentSeniorityCsv(repo).execute()

    df = make_df_from_record(record)

    fig = figure(title="Sample Plot")

    fig.add_tools(hov)

    script, div = components(fig)

    return render_template(
        "seniority/base_plot.html", resources=CDN.render(), script=script, div=div
    )


@blueprint.route("pilot_details/<int:id>")
def pilot_seniority_details(id):
    pass
