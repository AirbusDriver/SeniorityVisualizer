import pytest
from enum import auto, unique

from seniority_visualizer_app.user.role import Permissions, Role
from seniority_visualizer_app.user.utils import BaseTwoAutoEnum


@pytest.fixture
def bin_mapped_enum():
    @unique
    class SampleEnum(BaseTwoAutoEnum):
        A = auto()
        B = auto()
        c = auto()

    return SampleEnum


class TestBinaryMappedAutoEnum:
    def test_member(self, bin_mapped_enum):
        bm = bin_mapped_enum

        assert repr(bm.A) == "<SampleEnum.A>"
        assert 1 == bm.A
        assert bm.A == bm.A
        assert bm.A.bit_mask == '001'

    def test_bitwise(self, bin_mapped_enum):
        bm = bin_mapped_enum

        assert (bm.A | bm.B) == sum([bm.A, bm.B]) == 3


class TestRoles:
    def test_admin_role(self, db):
        admin = Role.query.filter(Role.name == "Admin").first()

        assert admin, "Admin not in db"

        for permission in Permissions:
            assert admin.has_permission(permission)

    def test_unconfirmed_user_role(self, db):
        unconfirmed = Role.query.filter(Role.name == "UnconfirmedUser").first()

        p = Permissions  # alias

        for perm in (
                p.VIEW_USER_DETAILS, p.EDIT_USER_DETAILS
        ):
            assert unconfirmed.has_permission(perm)

        unconfirmed_permissions = {
            p.EDIT_USER_DETAILS, p.VIEW_USER_DETAILS
        }

        excluded_permissions = set(Permissions).difference(unconfirmed_permissions)

        for perm in unconfirmed_permissions:
            assert unconfirmed.has_permission(perm)

        for perm in excluded_permissions:
            assert not unconfirmed.has_permission(perm)

        assert unconfirmed, "UnconfirmedUser not in db"

    def test_confirmed_user_role(self, db):
        confirmed = Role.query.filter(Role.name == "ConfirmedUser").first()

        assert confirmed, "ConfirmedUser not in db"
