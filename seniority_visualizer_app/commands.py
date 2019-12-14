# -*- coding: utf-8 -*-
"""Click commands."""
import os
from glob import glob
from subprocess import call
from pprint import pformat

import click

HERE = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.join(HERE, os.pardir)
TEST_PATH = os.path.join(PROJECT_ROOT, "tests")


@click.command()
def test():
    """Run the tests."""
    import pytest

    rv = pytest.main([TEST_PATH, "--verbose"])
    exit(rv)


@click.command()
@click.option(
    "-f",
    "--fix-imports",
    default=True,
    is_flag=True,
    help="Fix imports using isort, before linting",
)
@click.option(
    "-c",
    "--check",
    default=False,
    is_flag=True,
    help="Don't make any changes to files, just confirm they are formatted correctly",
)
def lint(fix_imports, check):
    """Lint and check code style with black, flake8 and isort."""
    skip = ["node_modules", "requirements", "migrations"]
    root_files = glob("*.py")
    root_directories = [
        name for name in next(os.walk("."))[1] if not name.startswith(".")
    ]
    files_and_directories = [
        arg for arg in root_files + root_directories if arg not in skip
    ]

    def execute_tool(description, *args):
        """Execute a checking tool with its arguments."""
        command_line = list(args) + files_and_directories
        click.echo("{}: {}".format(description, " ".join(command_line)))
        rv = call(command_line)
        if rv != 0:
            exit(rv)

    isort_args = ["-rc"]
    black_args = []
    if check:
        isort_args.append("-c")
        black_args.append("--check")
    if fix_imports:
        execute_tool("Fixing import order", "isort", *isort_args)
    execute_tool("Formatting style", "black", *black_args)
    execute_tool("Checking code style", "flake8")


@click.group(name="seniority")
def seniority_list():
    """Manage seniority lists directly"""
    pass


"""
Add a seniority record to the database from a tabular data file. The user can specify the path to read. The headers
in the file should correspond to the keys required to create the new record. The headers can be overridden by 
explicitly setting the headers. User can preview the seniority data about to be added with the --print option

Errors:
    * no file exists
    * file can not be read
    * file does not contain the minimum data or the headers have not been sufficiently specified to create PilotRecords


calls:

seniority add ./some/file_path.ext --valid date --header header attr --print
"""


@seniority_list.command()
@click.argument("file", type=click.File(mode="r"))
@click.option(
    "-h",
    "--header",
    type=str,
    nargs=2,
    multiple=True,
    help="specify column header with its mapped attr, ex -> cmid employee_id",
)
@click.option("--print", "echo", is_flag=True, default=False)
def add(file, header, echo):
    """
    Add seniority list from csv file
    """
    from seniority_visualizer_app.seniority.loader import SeniorityListLoader
    from seniority_visualizer_app.seniority.models import SeniorityListRecord
    from seniority_visualizer_app.seniority.serializer import SeniorityListSerializer

    headers = {file_key: desired for file_key, desired in header}

    loader = SeniorityListLoader(headers=headers)

    sen_list = loader.load_from_stream(file)

    if echo:
        data = SeniorityListSerializer().to_dict(sen_list)

        def pages():
            yield f"Published Date: {data['published_date']}"
            yield from (
                pformat({k: str(v) for k, v in row.items()}) + "\n"
                for row in data["pilots"]
            )

        click.echo_via_pager(pages())
        return None

    record = SeniorityListRecord.from_entity(sen_list)

    record.save()
