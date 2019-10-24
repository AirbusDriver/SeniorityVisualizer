import csv

# @classmethod
# def from_csv_file(
#     cls,
#     file_path,
#     published_date: Optional[datetime] = None,
#     row_to_pilot_factory: Optional[Callable[[dict], PilotRecord]] = None,
# ) -> SeniorityListRecord:
#     """
#     Return a new SeniorityListRecord instance from a csv file path. All child PilotRecord instances
#     are created upon reading their respective rows.
#     """
#     fp = Path(file_path)
#     if not fp.exists():
#         raise FileNotFoundError(f"{fp.resolve()} does not exist")
#
#     new_seniority_list_record = cls(published_date=published_date)
#
#     pilot_factory = row_to_pilot_factory or PilotRecord.from_dict
#
#     with open(fp, "r") as infile:
#         reader = csv.DictReader(infile)
#         rows = (row for row in reader)
#
#         for row in rows:
#             pilot_record = pilot_factory(row)
#             pilot_record.seniority_list = new_seniority_list_record
#
#     return new_seniority_list_record