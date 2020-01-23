import typing as t
from ..repo import ICsvRepo

if t.TYPE_CHECKING:
    from seniority_visualizer_app.seniority.entities import CsvRecord


class FilterSeniorityLists:
    """
    Filter SeniorityRecords
    """

    pass


class GetCurrentSeniorityCsv:
    """
    Retrieve the most recent seniority csv.
    """

    def __init__(self, repo: ICsvRepo):
        self.repo = repo

    def execute(self) -> "CsvRecord":
        records = self.repo.get_all()
        if not records:
            raise ValueError("no records in repository")

        return sorted(records, key=lambda r: r.published, reverse=True)[0]
