from click.testing import CliRunner


from seniority_visualizer_app.commands import seniority_list
from seniority_visualizer_app.seniority.models import SeniorityListRecord, PilotRecord


class TestSeniorityCommand:
    def test_add_command(self, clean_db, app):
        assert SeniorityListRecord.query.all() == []

        runner = app.test_cli_runner()

        result = runner.invoke(seniority_list, args=("add", ))

        assert 0, result.output