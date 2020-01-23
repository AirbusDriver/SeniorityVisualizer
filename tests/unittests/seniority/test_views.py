from unittest import mock

from flask import current_app

from seniority_visualizer_app.seniority import views
from seniority_visualizer_app.seniority.repo import ICsvRepo


def test_get_repo(app):
    """Get repo should, for now, simple return an in-memory repo from tests settings"""
    repo = views.get_repo(app)

    assert isinstance(repo, ICsvRepo)
    assert len(list(repo.get_all())) == 1

