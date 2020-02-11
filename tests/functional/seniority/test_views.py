"""Tests for the view functions"""
from unittest.mock import MagicMock, Mock

import pytest
from flask import url_for
from webtest import TestResponse, TestRequest

from seniority_visualizer_app.user.role import Permissions


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
