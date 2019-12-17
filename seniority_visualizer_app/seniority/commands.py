from pprint import pformat

import click
from flask.cli import with_appcontext


@click.command()
@click.argument("file", type=click.File(mode="r"))
@click.option(
    "-h",
    "--header",
    type=str,
    nargs=2,
    multiple=True,
    help="specify column header with its mapped attr, ex -> cmid employee_id",
)
@click.option("-p", "--published-date", type=click.DateTime())
@click.option("--print", "echo", is_flag=True, default=False)
@with_appcontext
def add(file, header, published_date, echo):
    """
    Add seniority list from csv file
    """
    from seniority_visualizer_app.seniority.loader import SeniorityListLoader
    from seniority_visualizer_app.seniority.models import SeniorityListRecord
    from seniority_visualizer_app.seniority.serializer import SeniorityListSerializer

    headers = {file_key: desired for file_key, desired in header}

    loader = SeniorityListLoader(headers=headers)

    try:
        sen_list = loader.load_from_stream(file)
    except Exception as e:
        raise click.UsageError(e)

    if echo:
        data = SeniorityListSerializer().to_dict(sen_list)

        def pages():
            yield f"Published Date: {data['published_date']}\n"
            yield from (
                pformat({k: str(v) for k, v in row.items()}) + "\n"
                for row in data["pilots"]
            )

        click.echo_via_pager(pages())
        return None

    record = SeniorityListRecord.from_entity(sen_list)
    record.published_date = published_date

    click.echo(f"Record created with published date: {record.published_date}")
    click.echo(f"Saving record")

    record.save()

    click.echo(f"Record saved!")
