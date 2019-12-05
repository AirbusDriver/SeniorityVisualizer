def test_seniority_list_from_csv_fixture(csv_senlist_pilot_records):
    """Verify seniority_list_from_csv fixture behaving predictably."""
    sen_list_record, _ = csv_senlist_pilot_records

    assert len(sen_list_record.pilots) == 3925
