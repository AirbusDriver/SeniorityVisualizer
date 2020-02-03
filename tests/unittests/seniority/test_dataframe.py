import pytest
import datetime as dt
import random
from io import StringIO

import pandas as pd
from pandas.core.dtypes import common as pd_common
import numpy as np

import seniority_visualizer_app.seniority.dataframe as loader


def test_fixture(standard_seniority_df):
    standardized = standard_seniority_df
    fields = loader.SeniorityDfFields

    assert pd_common.is_datetime64_dtype(standardized[fields.RETIRE_DATE])
    assert pd_common.is_int64_dtype(standardized[fields.SENIORITY_NUMBER])
    assert pd_common.is_string_dtype(standardized[fields.EMPLOYEE_ID])

