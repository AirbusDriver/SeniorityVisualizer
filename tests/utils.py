from pathlib import Path
from datetime import datetime, timezone
import csv
from typing import Union
from flask import url_for


TESTS_BASE_DIR = Path(__file__).parent
SAMPLE_CSV = TESTS_BASE_DIR.joinpath("sample.csv")


from seniority_visualizer_app.seniority.models import SeniorityListRecord, PilotRecord


def make_seniority_list_from_csv(sample_csv_path: Union[str, Path]):
    sen_list = SeniorityListRecord(
        published_date=datetime(2019, 7, 1, tzinfo=timezone.utc)
    )
    pilot_records = []

    if not isinstance(sample_csv_path, str):
        sample_csv_path = str(sample_csv_path)

    with open(sample_csv_path) as infile:
        reader = csv.DictReader(infile)

        for row in reader:
            record = PilotRecord(
                employee_id=row["cmid"].zfill(5),
                seniority_list=sen_list,
                hire_date=datetime.strptime(row["hire_date"], "%Y-%m-%d"),
                retire_date=datetime.strptime(row["retire_date"], "%Y-%m-%d"),
                literal_seniority_number=int(row["seniority_number"]),
                first_name=row["first_name"],
                last_name=row["last_name"],
                base=row["base"],
                aircraft=row["fleet"],
                seat=row["seat"],
            )
            pilot_records.append(record)

    return sen_list, pilot_records


def log_user_in(user, password, app):
    res = app.get(url_for("public.home"))
    form = res.forms["loginForm"]
    form["username"] = user.username
    form["password"] = password

    res = form.submit().maybe_follow()
    assert res.status_code == 200, "user unable to log in"

    return user
