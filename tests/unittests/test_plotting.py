import datetime as dt

import pytest

from seniority_visualizer_app.seniority import plotting as sen_plot


class TestGenerateDateIndices:
    """Tests for the date generation functions"""
    @pytest.mark.parametrize("start, end", [
        ("2000-01-01", "2001-01-01"),
        (dt.date(2000, 1, 1), dt.datetime(2001, 1, 1)),
        (dt.date(2000, 1, 1), dt.date(2001, 1, 1))
    ])
    def test_start_stop(self, start, end):
        gen_dates = sen_plot.generate_date_indices(start=start, end=end)

        _res = [dt.date(2000, i, 1) for i in range(1, 13)]
        _res.append(dt.date(2001, 1, 1))

        assert list(gen_dates) == _res

    def test_yield_overflow(self):
        start = "2000-1-1"
        end = "2000-3-1"

        res = list(sen_plot.generate_date_indices(start=start, end=end, yield_overflow=True))

        assert res == [
            dt.date(2000, 1, 1),
            dt.date(2000, 2, 1),
            dt.date(2000, 3, 1),
            dt.date(2000, 4, 1)
        ]