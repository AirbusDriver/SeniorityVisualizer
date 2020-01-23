import typing as t
import uuid

import pytest

from seniority_visualizer_app.seniority import repo
from seniority_visualizer_app.seniority.exceptions import RepositoryError
from tests import factories


@pytest.fixture
def csv_repo_in_memory_factory():
    def make_repo(
        records: int = 0
    ) -> t.Tuple[repo.CsvRepoInMemory, t.List[repo.CsvRecord]]:
        csv_records: t.List[repo.CsvRecord] = []
        if records > 0:
            csv_records = factories.CsvRecordFactory.build_batch(records)

        csv_repo = repo.CsvRepoInMemory(records=csv_records)

        return csv_repo, csv_records

    return make_repo


class TestCsvRepoInMemory:
    def test_empty_init(self, csv_repo_in_memory_factory):
        csv_repo, records = csv_repo_in_memory_factory()

        assert csv_repo._records == []
        assert csv_repo.get_all() == []

    def test_get_with_id(self, csv_repo_in_memory_factory):
        csv_repo, records = csv_repo_in_memory_factory(5)

        record = records[0]

        results = [
            csv_repo.get(record.id),
            csv_repo.get(str(record.id))
        ]

        assert all([record == r for r in results])

    def test_get_with_id_raises(self, csv_repo_in_memory_factory):
        csv_repo, records = csv_repo_in_memory_factory(5)

        bad_id = uuid.uuid4()

        with pytest.raises(ValueError, match=rf"no record with id: {bad_id}.*"):
            csv_repo.get(bad_id)

        with pytest.raises(ValueError, match=rf"no record with id: {bad_id}.*"):
            csv_repo.get(str(bad_id))

        with pytest.raises(TypeError):
            csv_repo.get(None)

    def test_save_on_empty(self, csv_repo_in_memory_factory):
        csv_repo, _ = csv_repo_in_memory_factory()

        new_record = factories.CsvRecordFactory.build()

        result = csv_repo.save(new_record)

        assert result == new_record.id
        assert csv_repo._records == [new_record]

    def test_save_on_populated(self, csv_repo_in_memory_factory):
        csv_repo, records = csv_repo_in_memory_factory(5)

        new_record = factories.CsvRecordFactory.build()

        result = csv_repo.save(new_record)

        assert result == new_record.id

        assert new_record in csv_repo._records

        overwriting = factories.CsvRecordFactory.build(id=new_record.id)

        with pytest.raises(ValueError, match=rf"record already.*"):
            csv_repo.save(overwriting)

        res = csv_repo.save(overwriting, overwrite=True)

        assert res == overwriting.id
        assert csv_repo.get(res) == overwriting
