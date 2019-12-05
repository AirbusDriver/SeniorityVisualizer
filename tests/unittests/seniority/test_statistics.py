from unittest import mock
from pathlib import Path

import pytest

from seniority_visualizer_app.seniority import statistics as stat
from seniority_visualizer_app.seniority import data_objects as do
from seniority_visualizer_app.seniority.entities import Pilot, SeniorityList


def test_calculate_pilot_seniority_status(pilot_dicts_from_csv):
    pilots = (Pilot.from_dict(d) for d in pilot_dicts_from_csv)
    sen_list = SeniorityList(pilots)

    pilot_1 = sen_list.sorted_pilot_data[0]

    assert stat.calculate_pilot_seniority_statistics(pilot_1, sen_list) == do.PilotSeniorityStatistics(
        current_seniority_number=1,
        hire_date=pilot_1.hire_date,
        retire_date=pilot_1.retire_date,
        employee_id=pilot_1.employee_id
    )

    pilot_3925 = sen_list.sorted_pilot_data[-1]

    assert stat.calculate_pilot_seniority_statistics(pilot_3925, sen_list) == do.PilotSeniorityStatistics(
        current_seniority_number=3925,
        hire_date=pilot_3925.hire_date,
        retire_date=pilot_3925.retire_date,
        employee_id=pilot_3925.employee_id
    )
