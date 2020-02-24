import pytest
import datetime as dt
import random
from io import StringIO

import pandas as pd
from pandas.core.dtypes import common as pd_common
import numpy as np

from seniority_visualizer_app.seniority.dataframe import STANDARD_FIELDS, require_fields


def test_fixture(standard_seniority_df):
    standardized = standard_seniority_df
    fields = STANDARD_FIELDS

    assert pd_common.is_datetime64_dtype(standardized[fields.RETIRE_DATE])
    assert pd_common.is_int64_dtype(standardized[fields.SENIORITY_NUMBER])
    assert pd_common.is_string_dtype(standardized[fields.EMPLOYEE_ID])


def test_require_fields():
    """Test `require_fields` decorator"""

    d = dict(
        key_01="some",
        key_02="test",
        key_03="dict",
    )

    df = pd.DataFrame(data=d, index=range(len(d)))

    def func_1(key_haver, *args, **kwargs):
        return True

    assert func_1(d)
    assert func_1(df)

    func_1 = require_fields("MISSING KEY")(func_1)

    exp_error_message = r"""function 'func_1' missing fields: \['MISSING KEY'\]"""

    with pytest.raises(KeyError, match=exp_error_message):
        func_1(d)

    d["MISSING KEY"] = True

    assert func_1(d)

    with pytest.raises(KeyError, match=exp_error_message):
        func_1(df)

    df["MISSING KEY"] = True

    assert func_1(df)
