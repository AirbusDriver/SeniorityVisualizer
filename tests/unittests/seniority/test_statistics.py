from unittest import mock
from pathlib import Path
import datetime as dt

import pytest
import pandas as pd

from seniority_visualizer_app.seniority import statistics as stat
from seniority_visualizer_app.seniority import data_objects as do
from seniority_visualizer_app.seniority.entities import Pilot, SeniorityList

fields = stat.FIELDS  # alias for brevity


def test_calculate_pilot_seniority_status(pilot_dicts_from_csv):
    pilots = (Pilot.from_dict(d) for d in pilot_dicts_from_csv)
    sen_list = SeniorityList(pilots)

    pilot_1 = sen_list.sorted_pilot_data[0]

    assert stat.calculate_pilot_seniority_statistics(
        pilot_1, sen_list
    ) == do.PilotSeniorityStatistics(
        current_seniority_number=1,
        hire_date=pilot_1.hire_date,
        retire_date=pilot_1.retire_date,
        employee_id=pilot_1.employee_id,
    )

    pilot_3925 = sen_list.sorted_pilot_data[-1]

    assert stat.calculate_pilot_seniority_statistics(
        pilot_3925, sen_list
    ) == do.PilotSeniorityStatistics(
        current_seniority_number=3925,
        hire_date=pilot_3925.hire_date,
        retire_date=pilot_3925.retire_date,
        employee_id=pilot_3925.employee_id,
    )


def test_pin_to_first_day():
    inp = pd.Timestamp("2020-05-06 12:34:00")

    assert stat.pin_to_first_day(inp) == pd.Timestamp("2020-05-01")
    assert stat.pin_to_first_day(inp, True) == pd.Timestamp("2020-05-01 12:34:00")

    inp = dt.date(2020, 5, 6)

    assert stat.pin_to_first_day(inp) == pd.Timestamp("2020-05-01")


def test_ffwd_and_pin():
    assert stat.ffwd_and_pin(pd.Timestamp("2020-05-06")) == pd.Timestamp("2020-06-01")
    assert stat.ffwd_and_pin(pd.Timestamp("2020-05-01")) == pd.Timestamp("2020-05-01")

    assert stat.ffwd_and_pin(pd.Timestamp("2020-12-31")) == pd.Timestamp("2021-01-01")


class TestMakeSeniorityPlotTimeSeries:
    def test_raises_for_missing_column(self, standard_seniority_df):
        with pytest.raises(ValueError, match=r"df missing .* column"):
            df = standard_seniority_df.loc[
                :, [fields.EMPLOYEE_ID, fields.SENIORITY_NUMBER]
            ]

            _ = stat.make_seniority_plot_date_index(df)

    def test_first(self, standard_seniority_df):
        with mock.patch(
            "seniority_visualizer_app.seniority.statistics.date"
        ) as mock_date:
            mock_date.today.return_value = dt.date(2020, 1, 15)

            res = stat.make_seniority_plot_date_index(standard_seniority_df, start=None, pin_to_first=False)

            assert res[0] == dt.date(2020, 1, 15)

            res = stat.make_seniority_plot_date_index(standard_seniority_df, start=None, pin_to_first=True)

            assert res[0] == dt.date(2020, 1, 1)


def test_pilots_remaining_series(standard_seniority_df):
    today = dt.date.today()

    start = dt.date(today.year, today.month, 1)
    end = standard_seniority_df[fields.RETIRE_DATE].max()

    dates = pd.date_range(start=start, end=end, freq="Y")

    res = stat.make_pilots_remaining_series(standard_seniority_df, dates)

    assert res is not None


def test_calculate_retirements_over_time():
    dates = ["2020-01-01", "2020-01-15", "2020-03-15", "2020-05-30"]

    data = pd.Series(map(lambda d: pd.Timestamp(d), dates))

    intervals = pd.interval_range(
        pd.Timestamp("2020-01-01"), pd.Timestamp("2020-06-01"), freq="MS", closed="left"
    )

    result = stat.calculate_retirements_over_time(data, intervals)

    assert result == [2, 0, 1, 0, 1]
    assert len(result) == len(intervals)
