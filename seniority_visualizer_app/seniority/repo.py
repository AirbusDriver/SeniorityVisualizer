import uuid
import typing as t

from .entities import CsvRecord


class ICsvRepo:
    def get(self, id: t.Union[str, uuid.UUID]) -> CsvRecord:
        raise NotImplementedError()

    def get_all(self) -> t.Iterable[CsvRecord]:
        raise NotImplementedError()

    def save(self, record: CsvRecord) -> uuid.UUID:
        raise NotImplementedError()


class CsvRepoInMemory(ICsvRepo):
    def __init__(self, records: t.Optional[t.Iterable[CsvRecord]] = None):
        self._records = list(records) if records is not None else []

    def __repr__(self):
        s = f"<{type(self).__name__}(records: {len(self._records)})>"
        return s

    def get(self, id: t.Union[str, uuid.UUID]) -> CsvRecord:
        """
        Return a CsvRecord from a str or uuid.UUID. Raise ValueError if not found.
        """
        if id is None:
            raise TypeError("id must be a string or uuid.UUID instance")
        if not isinstance(id, uuid.UUID):
            id = uuid.UUID(str(id))

        for rec in self._records:
            if rec.id == id:
                return rec
        raise ValueError(f"no record with id: {id}")

    def get_all(self) -> t.List[CsvRecord]:
        def key(rec: CsvRecord):
            return rec.published

        return sorted(self._records.copy(), key=key)

    def save(self, record: CsvRecord, overwrite=False) -> uuid.UUID:
        """
        Save record to the repo, return the uuid. Raise ValueError if the record exists
        in the repo already and overwrite is False.

        :param record: record to save
        :param overwrite: True if existing record should be overwritten,
        will raise ValueError if False as existing record found
        :return: uuid.UUID
        """
        try:
            existing_record = self.get(record.id)
        except ValueError:  # no record exists, save the new one
            self._records.append(record)
            return record.id
        else:  # record exists, check overwrite
            if overwrite:
                self._records.remove(existing_record)
                self._records.append(record)
                return record.id
            raise ValueError(f"record already exists with id: {existing_record.id}")
