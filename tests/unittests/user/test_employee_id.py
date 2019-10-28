import pytest

from seniority_visualizer_app.user.models import EmployeeID


class TestEmployeeID:
    @pytest.mark.parametrize(
        "inp, exp", [
            ("0123", "00123"),
            (123, "00123"),
            (" 123 ", "00123"),
        ],
        ids=[
            "str with extra 0 prefix",
            "int to string",
            "whitespaced"
        ]
    )
    def test_to_str(self, inp, exp):
        """
        EmployeeID returns expected format when casted to string
        """
        assert EmployeeID(inp).to_str() == exp

    @pytest.mark.parametrize(
        "inp_1, inp_2", [
            ("123", 123),
            ("", ""),
            (0, 0),
            ("00000123", "123"),
            ("123", "0000000000000000123"),
            ("  123  ", " 00123   "),
        ],
        ids=[
            "str to int",
            "'' to ''",
            "0 to 0",
            "long pre-padded string to normalized string",
            "normalized string to long pre-padded string",
            "whitespaced to differently whitespaced and padded"
        ]
    )
    def test_compare_emp_id_strings(self, inp_1, inp_2):
        emp_1 = EmployeeID(inp_1)
        emp_2 = EmployeeID(inp_2)

        assert emp_1 == emp_2
        assert emp_1 == inp_2
        assert emp_2 == inp_1
