import pytest

from seniority_visualizer_app.shared.entities import EmployeeID


class TestEmployeeID:
    @pytest.mark.parametrize(
        "inp, exp",
        [("0123", "00123"), (123, "00123"), (" 123 ", "00123")],
        ids=["str with extra 0 prefix", "int to string", "whitespaced"],
    )
    def test_to_str(self, inp, exp):
        """
        EmployeeID returns expected format when casted to string
        """
        assert EmployeeID(inp).to_str() == exp

    @pytest.mark.parametrize(
        "inp_1, inp_2",
        [
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
            "white spaced to differently white spaced and padded",
        ],
    )
    def test_compare_emp_id_strings(self, inp_1, inp_2):
        emp_1 = EmployeeID(inp_1)
        emp_2 = EmployeeID(inp_2)

        assert emp_1 == emp_2
        assert emp_1 == inp_2
        assert emp_2 == inp_1

    def test_compare_mixed_prefix(self):
        s1 = "JBU12345"
        s2 = "12345"

        EmployeeID.PREFIX = "JBU"

        assert EmployeeID(s1) == EmployeeID(s2) == "JBU12345"

        EmployeeID.LENGTH = 20

        assert EmployeeID(s1) == EmployeeID(s2) == "JBU12345"

        assert len(EmployeeID(s1).to_str()) == 20

    def test_hashing(self):
        emp = EmployeeID("12345")

        ids = {EmployeeID(i) for i in range(10)}

        assert not emp in ids

        ids.add(emp)

        assert emp in ids

        ids.remove(EmployeeID("12345"))

        assert not emp in ids
