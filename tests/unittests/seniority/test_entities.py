from datetime import date, timedelta, datetime
from random import shuffle
from typing import List
from unittest import mock

import pytest

from seniority_visualizer_app.seniority.entities import Pilot, SeniorityList
from seniority_visualizer_app.seniority.exceptions import SeniorityListError
from tests.factories import PilotFactory


class TestPilot:
    def test_pilot_is_senior_to(self):
        """
        Given two pilots, pilot1 hired before pilot2
        Then the first pilot is considered senior
        """
        pilot1: Pilot = PilotFactory(hire_date=date(1990, 1, 1))
        pilot2: Pilot = PilotFactory(hire_date=date(1991, 1, 1))

        assert pilot1.is_senior_to(pilot2)
        assert not pilot2.is_senior_to(pilot1)

        """
        Given two pilots hired on the same day
        And the second pilot retires after the first pilot
        Then the pilot retiring before the other pilot is considered more senior
        """
        pilot1.retire_date = date(2000, 1, 1)
        pilot2.hire_date = date(1990, 1, 1)
        pilot2.retire_date = date(2001, 1, 1)

        assert pilot1.is_senior_to(pilot2)
        assert not pilot2.is_senior_to(pilot1)

        """
        Given two pilots hired on the same day
        And the second pilot retires on the same day as the first
        And the second pilot has a higher literal seniority number assigned
        Then pilot1 is considered more senior
        """
        hd = date(1990, 1, 1)
        rd = date(2000, 1, 1)
        pilot1 = PilotFactory(hire_date=hd, retire_date=rd, literal_seniority_number=1)
        pilot2 = PilotFactory(hire_date=hd, retire_date=rd, literal_seniority_number=2)

        assert pilot1.is_senior_to(pilot2)
        assert not pilot2.is_senior_to(pilot1)

        """
        Given two pilots hired on the same day
        And the second pilot retires on the same day as the first
        And the second pilot does not have a literal seniority number assigned
        Then pilot1 is considered more senior
        """
        pilot2.literal_seniority_number = None

        assert pilot1.is_senior_to(pilot2)
        assert not pilot2.is_senior_to(pilot1)

    def test_pilot_hashing(self):
        pilots = PilotFactory.build_batch(10)

        pilot1 = pilots[0]

        p_set = set(pilots)

        assert pilot1 in pilots
        assert pilot1 in p_set
        assert len(p_set) == 10
        assert pilot1 is not pilots[1]

    def test_pilot_ordering(self):
        pilots: List[Pilot] = PilotFactory.build_batch(10)
        copied = pilots.copy()

        assert copied == pilots
        assert sorted(pilots) == pilots

        shuffle(pilots)

        assert not pilots == copied
        assert sorted(pilots) == copied

    def test_pilot_active_on(self):
        hired = date(2020, 1, 1)
        day_before_hired = hired - timedelta(days=1)
        retired = date(2030, 1, 1)
        day_before_retired = retired - timedelta(days=1)

        pilot = PilotFactory(hire_date=hired, retire_date=retired)

        assert not pilot.is_active_on(day_before_hired)
        assert pilot.is_active_on(hired)
        assert pilot.is_active_on(day_before_retired)
        assert not pilot.is_active_on(retired)

    def test_from_dict(self):
        info = {
            "hire_date": datetime(2020, 1, 1),
            "retire_date": datetime(2050, 1, 1),
            "employee_id": "12345",
            "literal_seniority_number": 10,
        }

        new_pilot = Pilot.from_dict(info)

        for k, v in info.items():
            if isinstance(v, datetime):
                v = v.date()
            assert getattr(new_pilot, k) == v


class TestSeniorityList:
    def test_instantiation_with_pilots(self):
        pilots = PilotFactory.build_batch(50)

        sen_list = SeniorityList(pilots)

        assert sen_list._pilots == pilots
        assert set(pilots) == set(sen_list._pilots)

        assert len(sen_list) == 50
        assert "len: 50" in repr(sen_list)

    def test_filter_active_on(self):
        rd = date(2050, 1, 1)
        class_1_hd = date(2000, 1, 1)
        class_2_hd = date(2010, 1, 1)
        class_1 = PilotFactory.build_batch(10, hire_date=class_1_hd, retire_date=rd)
        class_2 = PilotFactory.build_batch(10, hire_date=class_2_hd, retire_date=rd)

        all_pilots = [p for p in class_1]
        all_pilots.extend(class_2)

        sen_list = SeniorityList(all_pilots)

        assert len(set(sen_list.filter_active_on(class_1_hd - timedelta(days=1)))) == 0

        retrieved_class_1 = list(sen_list.filter_active_on(class_1_hd))
        retrieved_class_2 = list(sen_list.filter_active_on(class_2_hd))

        assert set(retrieved_class_1) == set(class_1)
        assert len(retrieved_class_1) == 10

        both = set(retrieved_class_1)
        both.update(set(retrieved_class_2))

        assert both == set(all_pilots)

        assert len(set(sen_list.filter_active_on(date(2060, 1, 1)))) == 0

    def test_get_pilot_index(self):
        """Test contains and _get_pilot_index"""
        pilots: List[Pilot] = PilotFactory.build_batch(100)

        sen_list = SeniorityList(pilots)

        target = pilots[50]

        from_dict = Pilot(
            employee_id=target.employee_id,
            hire_date=target.hire_date,
            retire_date=target.retire_date,
        )

        assert (
            sen_list._get_pilot_index(target, sen_list.pilot_data)
            == 50
            == sen_list._get_pilot_index(from_dict, sen_list.pilot_data)
        )

        assert target in sen_list

        with pytest.raises(ValueError):
            bad_pilot = mock.Mock(spec=Pilot)

            idx = sen_list._get_pilot_index(bad_pilot, sen_list.pilot_data)

        assert bad_pilot not in sen_list

    def test_lookup_pilot_seniority_number(self):

        pilot_sen = {i: p for i, p in enumerate(PilotFactory.build_batch(100), 1)}

        data = list(pilot_sen.values())
        shuffle(data)

        sen_list = SeniorityList(
            data
        )

        assert 1 == sen_list.lookup_pilot_seniority_number(pilot_sen[1])
        assert 100 == sen_list.lookup_pilot_seniority_number(pilot_sen[100])

        with pytest.raises(SeniorityListError):
            mock_pilot = mock.Mock(spec=Pilot)

            sen_list.lookup_pilot_seniority_number(mock_pilot)

        for i, pilot in pilot_sen.items():
            if i <= 50:
                pilot.is_active_on = mock.Mock(return_value=False)
            else:
                pilot.is_active_on = mock.Mock(return_value=True)

        assert sen_list.lookup_pilot_seniority_number(pilot_sen[51], date_=date(2050, 1, 1)) == 1
