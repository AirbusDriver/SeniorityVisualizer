"""
Module containing the data objects that pass between boundries.
"""
from typing import NamedTuple, Optional
from datetime import date


class SeniorityListSpan(NamedTuple):
    """Span of seniority"""

    earliest_hire: date
    latest_retire: date


class PilotSeniorityStatistics(NamedTuple):
    """Basic statistics about a pilot's membership in a seniority list"""

    current_seniority_number: Optional[int]
    hire_date: date
    retire_date: date
    employee_id: str


class SeniorityListStatistics(NamedTuple):
    """Basic statistics about a seniority list"""

    total_pilots: int
    valid_date: date
    most_recent_class: date
    total_retired: int
    span: SeniorityListSpan
