from typing import List, Union
from pathlib import Path
import uuid
import io


import pandas as pd
from flask import (
    Blueprint,
    make_response,
    render_template,
    current_app,
    Flask,
    request,
)
from flask_login import login_required, current_user

from ..extensions import cache

from .models import PilotRecord
from .utils import standardize_employee_id
from seniority_visualizer_app.user.models import Permissions
from .repo import CsvRepoInMemory, ICsvRepo
from .entities import CsvRecord
from . import statistics as stat
from .dataframe import STANDARD_FIELDS, make_standardized_seniority_dataframe
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
            "seniority/current_status.html", error="No records currently found"
        )
    else:
        response = render_template(
            "seniority/current_status.html", report=res.value, error=None
        )
        return response


@blueprint.route("retirements")
@cache.cached(3600, query_string=True)
def plot_retirements():
    """
    Present the base plot template
    """
    from bokeh.resources import CDN
    from bokeh.plotting import figure, ColumnDataSource, Figure
    from bokeh.embed import components
    from bokeh.models import HoverTool, LinearAxis, Range1d

    ROLLING = int(request.args.get("rolling_periods", 6))

    repo = get_repo(current_app)

    response = GetCurrentSeniorityCsv(repo).execute(
        uc.requests.SeniortyFilterRequest(all=True)
    )

    if not response:
        return render_template("seniority/base_plot.html", errors=True)

    else:
        record: CsvRecord = response.value[-1]

    df = make_df_from_record(record)

    INTERVALS = pd.interval_range(
        start=pd.Timestamp(record.published),
        end=stat.ffwd_and_pin(df[STANDARD_FIELDS.RETIRE_DATE].max()),
        freq="MS",
        closed="left",
    )

    retirements = stat.calculate_retirements_over_time(
        df[STANDARD_FIELDS.RETIRE_DATE], INTERVALS
    )

    retire_data = pd.DataFrame(data=dict(retirements=retirements), index=INTERVALS.left)
    retire_data.index.name = "date"

    retire_data["rolling"] = retire_data["retirements"].rolling(window=ROLLING).mean()
    retire_data["remaining"] = len(df) - retire_data["retirements"].cumsum()

    source = ColumnDataSource(retire_data)

    fig: Figure = figure(
        title="Remaining Pilots",
        x_axis_type="datetime",
        plot_height=600,
        plot_width=1200,
        y_range=(0, retire_data[["retirements", "rolling"]].max().max() * 1.1),
    )

    fig.circle(
        x="date",
        y="retirements",
        source=source,
        alpha=0.2,
        legend_label="Retirements this calendar month",
    )
    fig.line(
        x="date",
        y="rolling",
        source=source,
        legend_label=f"Mean retirements/month last {ROLLING} months",
    )
    fig.extra_y_ranges = dict(remaining=Range1d(start=0, end=len(df) * 1.05))

    fig.add_layout(LinearAxis(y_range_name="remaining"), "right")
    fig.legend.click_policy = "hide"

    fig.line(
        x="date",
        y="remaining",
        source=source,
        legend_label="Remaining active pilots",
        y_range_name="remaining",
    )

    hov = HoverTool(
        tooltips=[
            ("Date", "@date{%F}"),
            ("Retirements", "@retirements"),
            (f"Avg last {ROLLING} months", "@rolling"),
            ("Remaining", "@remaining"),
        ],
        formatters={"date": "datetime"},
    )

    fig.add_tools(hov)

    script, div = components(fig)

    description = render_template(
        "seniority/descriptions/retirements.html",
        max_retirements=retire_data["retirements"].max(),
        max_retirements_month=retire_data["retirements"][
            retire_data["retirements"] == retire_data["retirements"].max()
        ].index[0].date(),
    )

    return render_template(
        "seniority/base_plot.html",
        resources=CDN.render(),
        script=script,
        div=div,
        description=description,
    )


@blueprint.route("pilot_details/<int:id>")
def pilot_seniority_details(id):
    pass
