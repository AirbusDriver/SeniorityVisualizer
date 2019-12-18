import typing as t
from seniority_visualizer_app.shared.request_object import (
    ValidRequestObject,
    InvalidRequestObject,
)


class SeniortyFilterRequest(ValidRequestObject):
    def __init__(self, all: bool = True, most_recent: bool = False):
        self.all = all
        self.most_recent = most_recent

    @classmethod
    def from_dict(
        cls, adict: t.Dict[str, t.Any]
    ) -> t.Union["SeniortyFilterRequest", InvalidRequestObject]:
        invalid = InvalidRequestObject()

        if adict.get("all"):
            return cls(all=True, most_recent=False)

        most_recent = adict.get("most_recent")

        if most_recent is None:
            invalid.add_error("most_recent", "must be a bool")

        if invalid.has_errors():
            return invalid

        return cls(most_recent=True, all=False)


class SeniorityReportRequest(ValidRequestObject):
    def __init__(self, use_current: bool = True):
        self.use_current = use_current

    @classmethod
    def from_dict(
        cls, adict: t.Dict[str, t.Any]
    ) -> t.Union["SeniorityReportRequest", "InvalidRequestObject"]:
        use_current = adict.get("use_current", True)

        invalid = InvalidRequestObject()

        if not isinstance(use_current, bool):
            invalid.add_error("use_current", "'use_current' must be a boolean value")

        if invalid.has_errors():
            return invalid
        else:
            return cls(use_current=use_current)
