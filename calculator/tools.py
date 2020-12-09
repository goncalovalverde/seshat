import pandas as pd


def group_by_date(cycle_data, index) -> pd.DataFrame:
    """Group information in cycle_date by date and use index as index"""
    table = pd.pivot_table(
        cycle_data,
        values="Key",
        index=[index],
        columns="Type",
        fill_value=0,
        aggfunc="count",
    )
    df = pd.DataFrame(table.to_records())
    df = df.resample("D", on=index).sum()
    df["Total"] = df.sum(axis=1)
    return df
