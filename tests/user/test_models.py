# -*- coding: utf-8 -*-
"""Model unit tests."""
import datetime as dt

import pytest

from seniority_visualizer_app.user.models import User
from seniority_visualizer_app.user.role import Role

from tests.factories import UserFactory


@pytest.mark.usefixtures("clean_db")
class TestUser:
    """User tests."""

    def test_get_by_id(self):
        """Get user by ID."""
        user = User("foo", "test@email.com", "foo@bar.com")
        user.save()

        retrieved = User.get_by_id(user.id)
        assert retrieved == user

    def test_created_at_defaults_to_datetime(self):
        """Test creation date."""
        user = User(username="foo", personal_email="test", company_email="foo@bar.com")
        user.save()
        assert bool(user.created_at)
        assert isinstance(user.created_at, dt.datetime)

    def test_password_is_nullable(self):
        """Test null password."""
        user = User(username="foo", personal_email="test", company_email="foo@bar.com")
        user.save()
        assert user.password is None

    def test_factory(self, clean_db):
        """Test user factory."""
        user = UserFactory(password="myprecious")
        clean_db.session.commit()
        assert bool(user.username)
        assert bool(user.personal_email)
        assert bool(user.company_email)
        assert bool(user.created_at)
        assert user.is_admin is False
        assert user.active is True
        assert user.check_password("myprecious")

    @pytest.mark.parametrize(
        "inp_email, query_email",
        [
            ("thomas.jefferson@example.com", "thomas.jefferson@example.com"),
            ("thomas.jefferson@example.com", "Thomas.Jefferson@example.com"),
        ],
    )
    def test_filter_by_email_case_insensitive(self, inp_email, query_email, clean_db):
        """User email lookups """
        user = UserFactory(company_email=inp_email)

        user.save()
        clean_db.session.commit()

        retrieved = User.get_by_email(
            User.company_email, query_email, case_insensitive=True
        )

        assert retrieved == user

    @pytest.mark.parametrize(
        "inp_email, query_email, match",
        [
            ("thomas.jefferson@example.com", "thomas.jefferson@example.com", True),
            ("THOMAS.jefferson@example.com", "thomas.jefferson@example.com", False),
        ],
    )
    def test_filter_by_email_case_sensitive(self, inp_email, query_email, match, clean_db):
        """User email lookups """
        user = UserFactory(company_email=inp_email)

        user.save()
        clean_db.session.commit()

        retrieved = User.get_by_email(
            User.company_email, query_email, case_insensitive=False
        )

        if match:
            assert retrieved == user
        else:
            assert retrieved is None

    def test_check_password(self):
        """Check password."""
        user = User.create(
            username="foo",
            personal_email="test@email.com",
            company_email="test@test.com",
            password="foobarbaz123",
        )
        assert user.check_password("foobarbaz123") is True
        assert user.check_password("barfoobaz") is False

    def test_full_name(self):
        """User full name."""
        user = UserFactory(first_name="Foo", last_name="Bar")
        assert user.full_name == "Foo Bar"

    def test_roles(self):
        """Add a role to a user."""
        role = Role(name="admin")
        role.save()
        user = UserFactory()
        user.role = role
        user.save()
        assert role == user.role
