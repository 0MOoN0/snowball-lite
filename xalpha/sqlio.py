from __future__ import annotations

import pandas as pd
from sqlalchemy import exc, inspect as sa_inspect

SQL_BACKEND_READ_ERRORS = (
    exc.ProgrammingError,
    exc.OperationalError,
    exc.NoSuchTableError,
)

CACHE_BACKEND_MISS_ERRORS = (FileNotFoundError, KeyError) + SQL_BACKEND_READ_ERRORS


def read_sql_table_compat(table_name, con):
    inspector = sa_inspect(con)
    if not inspector.has_table(table_name):
        raise exc.NoSuchTableError(table_name)
    return pd.read_sql_table(table_name, con)


def normalize_sql_date_column(df, column="date"):
    if column not in df.columns:
        return df

    if pd.__version__[0] == "1":
        df[column] = pd.to_datetime(df[column])
    else:
        df[column] = pd.to_datetime(df[column], format="mixed")

    return df
