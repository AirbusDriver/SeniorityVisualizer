from typing import Union, List, Callable


def standardize_employee_id(employee_id: Union[int, str]) -> str:
    """Return a standardized employee_id"""
    if employee_id is None or employee_id == "":
        raise ValueError("employee_id can not be None or an empty string")

    _id = str(employee_id)

    transformations: List[Callable[[str], str]] = [
        lambda s: s.zfill(16),
        str.upper,
    ]

    for trans in transformations:
        _id = trans(_id)
    return _id
