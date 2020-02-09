"""
Module handling the creation of the standard dataframe that statistical and plotting
code will use.
"""
import typing as t
from functools import wraps

import pandas as pd


class SeniorityDfFields:
    """
    Class containing the fields of a standard seniority list

    These fields are used as standard column reference names that contain simple
    strings of their attribute name. This allows for dataframes created by the
    :func:`make_standardized_seniority_dataframe` to be used with `SeniorityDfFields.ATTR`
    """

    SENIORITY_NUMBER = "SENIORITY_NUMBER"
    RETIRE_DATE = "RETIRE_DATE"
    BASE = "BASE"
    SEAT = "SEAT"
    EMPLOYEE_ID = "EMPLOYEE_ID"
    FLEET = "FLEET"

    @classmethod
    def all(cls):
        return iter(cls())

    def __iter__(self):
        return iter(
            [
                self.SENIORITY_NUMBER,
                self.RETIRE_DATE,
                self.BASE,
                self.SEAT,
                self.EMPLOYEE_ID,
                self.FLEET,
            ]
        )


def standardize_seniority_df_names(
    df: pd.DataFrame, fields: t.Dict[str, str]
) -> pd.DataFrame:
    """
    Return a dataframe with standardized names that are renamed according to the
    `fields` parameter. The `fields` parameter should be map containing the original
    column name as the key, with the corresponding attribute of `SeniorityDfFields`.
    If any required keys are missing, a `ValueError` will be raised.

    Example::

        fields = {
            "cmid": SeniorityDfFields.EMPLOYEE_ID,
            "sen": SeniorityDfFields.SENIORITY_NUMBER,
            }

    """
    rename_map = {orig: field for orig, field in fields.items()}

    standardized: pd.DataFrame = df.rename(columns=rename_map)

    missing_keys = set(SeniorityDfFields.all()).difference(
        set(standardized.columns.to_list())
    )

    if missing_keys:
        raise ValueError(f"missing keys: {missing_keys}")

    return standardized


def make_standardized_seniority_dataframe(
    df: pd.DataFrame, fields: t.Dict[str, str]
) -> pd.DataFrame:
    """
    Return a new dataframe with overridden fields.

    :param fields: dict containing current_column:SeniorityDfField pairs, see
    `standardize_seniority_df_names`
    """

    renamed = standardize_seniority_df_names(df, fields)

    renamed[SeniorityDfFields.RETIRE_DATE] = pd.to_datetime(
        renamed[SeniorityDfFields.RETIRE_DATE]
    )

    renamed[SeniorityDfFields.EMPLOYEE_ID] = renamed[
        SeniorityDfFields.EMPLOYEE_ID
    ].astype(str)

    return renamed


def require_fields(*fields):
    """
    Raise a KeyError if a function is called with a missing field. The
    first index of the function should be the target parameter.

    Usage:
        >>> def some_func(df, *args, **kwargs):
        ...     print("did stuff")
        >>> d = dict(some_key="test", other="data")
        >>> some_func(d)
        did stuff

    Now with the decorator applied

        >>> @require_fields("some_other_key")
        ... def some_func(df, *args, **kwargs):
        ...     print("did stuff")
        >>> some_func(d)
        Traceback (most recent call last):
        ...
        KeyError: "function 'some_func' missing fields: ['some_other_key']"
    """
    def decorator(func):
        @wraps(func)
        def wrapper(df: pd.DataFrame, *args, **kwargs):
            keys = set(df.keys())
            require = set(fields)
            missing = require.difference(keys)
            if missing:
                raise KeyError(f"function '{func.__name__}' missing fields: {list(missing)}")
            return func(df, *args, **kwargs)
        return wrapper
    return decorator




STANDARD_FIELDS = SeniorityDfFields()