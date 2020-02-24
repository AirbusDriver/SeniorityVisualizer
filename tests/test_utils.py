import pytest

from datetime import date, datetime

from seniority_visualizer_app.utils import cast_date, to_iso


class TestToIso:
    @pytest.mark.parametrize(
        "inp, exp",
        [
            ("2000-01-01", "2000-01-01"),
            ("2000-1-1", "2000-01-01"),
            ("2000/1/1", "2000-01-01"),
            ("2000-01-01T10:20:30", "2000-01-01T10:20:30"),
            ("2000-01-01 10:20:30.12345", "2000-01-01T10:20:30.12345"),
            ("2000-01-01 10:20", "2000-01-01T10:20"),
        ],
    )
    def test_regex(self, inp, exp):
        assert to_iso(inp) == exp

    @pytest.mark.parametrize("inp", ["2020-01", "20-12-12", "2020-1-1T"])
    def test_raises_value_error(self, inp):
        with pytest.raises(ValueError, match=rf"Invalid isoformat string: {inp}"):
            to_iso(inp)


class TestCastDate:
    @pytest.mark.parametrize(
        "inp",
        [
            date(2020, 6, 15),
            datetime(2020, 6, 15),
            datetime(2020, 6, 15, 10, 20),
            "2020-6-15",
            "2020-06-15 10:20:15",
        ],
    )
    def test_good_input(self, inp):
        exp = date(2020, 6, 15)

        result = cast_date(inp)

        assert result == exp
