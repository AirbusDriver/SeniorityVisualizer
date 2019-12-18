from seniority_visualizer_app.user.models import User, Role


def test_seniority_list_from_csv_fixture(csv_senlist_pilot_records):
    """Verify seniority_list_from_csv fixture behaving predictably."""
    sen_list_record, _ = csv_senlist_pilot_records

    assert len(sen_list_record.pilots) == 3925


def test_confirmed_user(confirmed_user):
    user: User = confirmed_user

    assert user.role.name == "ConfirmedUser"
    assert user.active
    assert user.is_active
    assert not user.is_anonymous
    assert user.is_authenticated
    assert user.personal_email_confirmed
    assert user.company_email_confirmed
