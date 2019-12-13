from typing import Union, List, Callable

from seniority_visualizer_app.shared.entities import EmployeeID


def standardize_employee_id(employee_id: Union[int, str, EmployeeID]) -> str:
    """Return a standardized employee_id"""
    if not isinstance(employee_id, EmployeeID):
        employee_id = EmployeeID(employee_id)
    return employee_id.to_str()
