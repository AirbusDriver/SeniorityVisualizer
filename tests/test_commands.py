from seniority_visualizer_app.commands import add
from seniority_visualizer_app.seniority.models import SeniorityListRecord, PilotRecord

from .utils import SAMPLE_CSV


class TestSeniorityCommand:
    def test_add_command(self, clean_db, app):
        assert SeniorityListRecord.query.all() == []

        runner = app.test_cli_runner()

        args = " ".join(
            [
                str(SAMPLE_CSV),
                "-h",
                "cmid",
                "employee_id",
                "-h",
                "seniority_number",
                "literal_seniority_number",
                "-p",
                "2000-01-01",
            ]
        )

        result = runner.invoke(add, args=args)

        assert result.exit_code == 0
