from unittest import mock

import pytest
from flask import url_for
from webtest import TestResponse

from seniority_visualizer_app.seniority.repo import ICsvRepo
from seniority_visualizer_app.user.role import Permissions


def test_get_repo(app):
    """Get repo should, for now, simple return an in-memory repo from tests settings"""
    from seniority_visualizer_app.seniority import views

    repo = views.get_repo(app)

    assert isinstance(repo, ICsvRepo)
    assert len(list(repo.get_all())) == 1


@mock.patch("seniority_visualizer_app.seniority.views.get_repo")
def test_current_status_failure(mock_get_repo, testapp, confirmed_user):
    """Test the current status page renders error"""

    mock_get_repo.return_value = None

    res: TestResponse = testapp.get(
        url_for("seniority.current_status"), expect_errors=False
    )

    res.mustcontain("No records currently found")


def test_current_status_success(testapp, confirmed_user):
    """Test the current status page renders seniority list report"""

    res: TestResponse = testapp.get(
        url_for("seniority.current_status"), expect_errors=False
    )

    res.mustcontain(
        "Total Pilots: 3925",
        "Published Date: 01 Jan, 2020",
        "Retired Since Published:",
        "Latest Retirement: 05 May, 2059",
        no=["No records currently found"],
    )


class TestPermissions:
    def test_non_confirmed_user_shown_401(self, logged_in_user, testapp):
        """
        A user without VIEW_SENIORITY_DATA should be shown 401 when attempting
        access to seniority endpoints.
        """

        assert not logged_in_user.role.has_permission(
            Permissions.VIEW_SENIORITY_DATA
        )

        res: TestResponse = testapp.get(url_for("seniority.current_status"), expect_errors=True)

        assert res.status_code == 401

        logged_in_user.role.add_permission(
            Permissions.VIEW_SENIORITY_DATA
        )

        res: TestResponse = testapp.get(url_for("seniority.current_status"), expect_errors=True)

        assert res.status_code == 200


@pytest.mark.usefixtures("confirmed_user", "app")
class TestViews:
    @pytest.mark.parametrize("endpoint,args", [
        ("seniority.current_status", {}),
        ("seniority.plot_retirements", {}),
        ("seniority.pilot_plot", {"emp_id": 78629}),
    ])
    def test_status(self, endpoint, args, testapp):
        """Test endpoints return 200 status"""
        res: TestResponse = testapp.get(url_for(endpoint, **args))

        assert res.status_code == 200