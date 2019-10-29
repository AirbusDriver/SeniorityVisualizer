"""Tests for the view functions"""
from unittest.mock import MagicMock, Mock

import pytest
from flask import url_for
from webtest import TestResponse, TestRequest

from seniority_visualizer_app.user.role import Permissions


class TestPermissions:
    def test_non_confirmed_user_shown_401(self, logged_in_user, testapp, seniority_list_from_csv):
        """
        A user without VIEW_SENIORITY_DATA should be shown 401 when attempting
        access to seniority endpoints.
        """
        seniority_list_from_csv.save()
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
