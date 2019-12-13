from __future__ import annotations
from typing import Union, Any


# todo: add comparison functions
class EmployeeID:
    """Standardize behavior and comparison of employee IDs"""

    LENGTH = 5
    FRONT_PAD_CHAR = "0"
    PREFIX = None
    CASE = "upper"

    def __init__(self, id: Union[str, int, EmployeeID]):
        if isinstance(id, EmployeeID):
            id = id.to_str()
        self._id = str(id)

    def __eq__(self, other: Any) -> bool:
        if other is None:
            raise TypeError("other can not be NoneType")
        if not isinstance(other, EmployeeID):
            other_str = EmployeeID(other).to_str()
        else:
            other_str = other.to_str()

        return self.to_str() == other_str

    def __hash__(self):
        return hash(self.to_str())

    def __str__(self) -> str:
        return self.to_str()

    def __repr__(self):
        return f"{type(self).__name__}({repr(self._id)})"

    def _pad_id(self, _id: str) -> str:
        """Add padding to the front of ID until desired length if not already added"""
        out = _id

        if self.PREFIX and not _id.startswith(self.PREFIX):
            out = self.PREFIX + out

        if self.LENGTH and len(out) < self.LENGTH:
            n_pad = self.LENGTH - len(out)
            assert n_pad >= 1

            pad_str = self.FRONT_PAD_CHAR * n_pad
            out = pad_str + out

        # remove padded characters from front of string
        if self.LENGTH and len(out) > self.LENGTH:
            n_pad_to_remove = len(out) - self.LENGTH
            if out[:n_pad_to_remove] == self.FRONT_PAD_CHAR * n_pad_to_remove:
                out = out[n_pad_to_remove:]

        return out

    def _pre_format(self, _id: str) -> str:
        """
        Adjust the character content of the string, i.e. handle padding or strip
        whitespace.
        """
        out = _id
        out = out.strip()
        out = self._pad_id(out)

        return out

    def _format(self, _id: str) -> str:
        """Reformatting hook"""
        out = _id

        return out

    def _post_format(self, _id: str) -> str:
        """Add final formatting to ID"""
        out = _id

        out = self._apply_case(out)
        return out

    def _apply_case(self, _id: str) -> str:
        """Apply case setting to id string"""
        out = _id

        cases = {
            "upper": str.upper,
            "lower": str.lower,
        }
        case_callable = cases.get(self.CASE)

        if case_callable:
            out = case_callable(out)

        return out

    def to_str(self) -> str:
        """Return the final formatted ID"""
        out = str(self._id)

        out = self._pre_format(out)
        out = self._format(out)
        out = self._post_format(out)

        return out