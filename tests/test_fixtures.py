def test_seniority_list_from_csv_fixture(seniority_list_from_csv):
    """Verify seniority_list_from_csv fixture behaving predictably."""
    sen_list_record = seniority_list_from_csv

    assert len(sen_list_record.pilots) == 3925