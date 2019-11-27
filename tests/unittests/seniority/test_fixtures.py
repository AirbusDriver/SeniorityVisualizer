def test_populated_seniority_list_fixture(populated_seniority_list):
    """Verify populated_seniority_list fixture_behaving predictably."""
    pilots = populated_seniority_list.pilots

    assert len(pilots) == 100

    for a, b in zip(pilots[:-1], pilots[1:]):
        assert a.hire_date <= b.hire_date and a.retire_date <= b.retire_date
        assert a.seniority_list.id == populated_seniority_list.id == 1