from logging import exception
import pandas as pd
import logging
import numpy as np
from pandas.core.frame import DataFrame
import calculator.tools


def cycle_data(data: DataFrame, config: dict) -> DataFrame:
    """
    Calculate the lead time and cycle time for the given data and configuration.

    :param data: The input data
    :type data: DataFrame
    :param config: The configuration dictionary
    :type config: dict
    :return: The DataFrame with added lead time and cycle time
    :rtype: DataFrame
    """
    # get the first element of the workflow
    # to know where to start calculating the lead time
    workflow_keys = list(config["Workflow"].keys())
    start_column = workflow_keys[0]
    end_column = workflow_keys[-1]

    # start = "Created"

    # adding lead time to cycle_data
    cycle_data = lead_time(data, start_column, end_column)

    # adding cycle_time (between workflow steps) to cycle_data
    for i, start in enumerate(workflow_keys[:-1]):
        end = workflow_keys[i + 1]
        cycle_time(cycle_data, start, end)

    return cycle_data


# Productivity - How Much - "Do Lots"
def throughput(cycle_data: DataFrame, end_column: str) -> DataFrame:
    """Create a new Data Frame with the throughput information. The throughput is calculated
    by grouping the cycle data by date for the specified end column.

    :param cycle_data: The cycle_data
    :type cycle_data: DataFrame
    :param end_column: The name of the end state of the work flow
    :type end_column: str
    :return: The DataFrame with the Throughput
    :rtype: DataFrame
    """

    # Force int16 type to reduce memory
    throughput = calculator.tools.group_by_date(cycle_data, end_column).astype("int16")
    # throughput = throughput.set_index("Done")

    return throughput


def velocity(cycle_data: DataFrame, end_column: str) -> DataFrame:
    """
    Calculate the velocity of the cycle data. The velocity is calculated
    by summing the story points for each type of work item per day.

    :param cycle_data: The cycle data
    :type cycle_data: DataFrame
    :param end_column: The name of the end state of the work flow
    :type end_column: str
    :return: The DataFrame with the velocity
    :rtype: DataFrame
    """

    table = pd.pivot_table(
        cycle_data,
        values="Story Points",
        index=[end_column],
        columns="Type",
        fill_value=0,
        aggfunc="sum",
    )
    df = pd.DataFrame(table.to_records())
    df = df.resample("D", on=end_column).sum()
    df["Total"] = df.sum(axis=1)
    return df


def story_points(cycle_data: DataFrame, end_column: str) -> DataFrame:
    """
    Calculate the story points of the cycle data. The story points are calculated
    by counting the number of keys for each type of story point per day.

    :param cycle_data: The cycle data
    :type cycle_data: DataFrame
    :param end_column: The name of the end state of the work flow
    :type end_column: str
    :return: The DataFrame with the story points
    :rtype: DataFrame
    """
    table = pd.pivot_table(
        cycle_data,
        values="Key",
        index=end_column,
        columns="Story Points",
        fill_value=0,
        aggfunc="count",
    )
    df = pd.DataFrame(table.to_records())
    df = df.resample("D", on=end_column).sum()
    df["Total"] = df.sum(axis=1)
    return df


# Responsiveness - How Fast - "Do it Fast"
def lead_time(cycle_data: DataFrame, start_column: str, end_column: str) -> DataFrame:
    """
    Calculate the lead time of the cycle data. The lead time is calculated
    by subtracting the start column from the end column.

    :param cycle_data: The cycle data
    :type cycle_data: DataFrame
    :param start_column: The name of the start state of the work flow
    :type start_column: str
    :param end_column: The name of the end state of the work flow
    :type end_column: str
    :return: The DataFrame with the lead time
    :rtype: DataFrame
    """
    logging.debug("Calculating lead time for %s", start_column)
    try:
        cycle_data["Lead Time"] = cycle_data[end_column] - cycle_data[start_column]
        cycle_data["Lead Time"] = pd.to_numeric(
            cycle_data["Lead Time"].dt.days, downcast="integer"
        )
        # Force int16 type to reduce memory consumption
        # cycle_data["Lead Time"] = cycle_data["Lead Time"].astype(pd.Int16Dtype())
        return cycle_data
    except KeyError as e:
        logging.error("No data found for %s", str(e))
        logging.error("Are you sure you configured your workflow correctly?")
        return cycle_data


# TODO: migrate this to multi header df (and apply it to all dataframe )
def cycle_time(cycle_data: DataFrame, start: str, end: str) -> DataFrame:
    """
    Calculate the cycle time of the cycle data. The cycle time is calculated
    by subtracting the start column from the end column.

    :param cycle_data: The cycle data
    :type cycle_data: DataFrame
    :param start: The name of the start state of the work flow
    :type start: str
    :param end: The name of the end state of the work flow
    :type end: str
    :return: The DataFrame with the cycle time
    :rtype: DataFrame
    """
    logging.debug("Calculating cycle time for start:" + start + " and end:" + end)
    try:
        column = "Cycle Time " + start
        cycle_data[column] = cycle_data[end] - cycle_data[start]
        cycle_data[column] = pd.to_numeric(
            cycle_data[column].dt.days, downcast="integer"
        )
        # Force int16 type to reduce memory consumption
        # cycle_data[column] = cycle_data[column]  # .astype(pd.Int16Dtype())
        return cycle_data
    except KeyError as e:
        logging.error("No data found for %s", str(e))
        logging.error("Are you sure you configured your workflow correctly?")
        return cycle_data


def avg_lead_time(cycle_data: DataFrame, pbi_type: str, end_column: str) -> DataFrame:
    """
    Calculate the average lead time of the cycle data. The average lead time is calculated
    by grouping the data by the end column and taking the mean.

    :param cycle_data: The cycle data
    :type cycle_data: DataFrame
    :param pbi_type: The type of PBI to filter by
    :type pbi_type: str
    :param end_column: The name of the end state of the work flow
    :type end_column: str
    :return: The DataFrame with the average lead time
    :rtype: DataFrame
    """    
    try:
        lead_time = cycle_data[[end_column, "Type", "Lead Time"]].copy()

        if pbi_type != "Total":
            lead_time = lead_time.loc[lead_time["Type"] == pbi_type]

        lead_time = lead_time.groupby(end_column).mean()
        lead_time = lead_time.resample("W").mean()
        lead_time = lead_time.fillna(0)
        return lead_time
    except KeyError as e:
        logging.error("No data found for %s", str(e))
        logging.error("Are you sure you configured your workflow correctly?")
        return cycle_data


# Predictability - How Repeatable - "Do it Predictably"
def net_flow(cycle_data: DataFrame, start: str, end, pbi_type: str) -> pd.DataFrame:
    """
    Calculate the net flow of the cycle data. The net flow is calculated
    by subtracting the number of created items from the number of done items.

    :param cycle_data: The cycle data
    :type cycle_data: DataFrame
    :param start: The name of the start state of the work flow
    :type start: str
    :param end: The name of the end state of the work flow
    :type end: str
    :param pbi_type: The type of PBI to filter by
    :type pbi_type: str
    :return: The DataFrame with the net flow
    :rtype: DataFrame
    """
    try:
        created = calculator.tools.group_by_date(cycle_data, start)
        done = calculator.tools.group_by_date(cycle_data, end)

        net_flow_data = pd.merge(created, done, left_index=True, right_index=True, how="outer")
        net_flow_data = net_flow_data.fillna(0)
        # Net Flow : Done items - Created items
        net_flow_data["Net Flow"] = net_flow_data[pbi_type + "_y"] - net_flow_data[pbi_type + "_x"]
        # WIP : Amount of items still in progress.
        # We calculate this using cumulative sum
        net_flow_data["WIP"] = (
            net_flow_data[pbi_type + "_x"].cumsum() - net_flow_data[pbi_type + "_y"].cumsum()
        )
        net_flow_data = net_flow_data.fillna(0)

        return net_flow_data
    except KeyError as e:
        logging.error("No data found for %s", str(e))
        logging.error("Are you sure you configured your workflow correctly?")
        return cycle_data


def wip(cfd_data) -> pd.DataFrame:
    return pd.DataFrame(
        {"WIP": cfd_data["Created"] - cfd_data["Done"]}, index=cfd_data.index
    )


def cfd(cycle_data: DataFrame, workflow: dict, pbi_type: str = "Total") -> DataFrame:
    cycle_names = [s for s in workflow]
    # cycle_names.insert(0, "Created")
    cfd_data = cycle_data

    if pbi_type != "Total":
        cfd_data = cfd_data.loc[cfd_data["Type"] == pbi_type]

    cfd_data = cfd_data[cycle_names]

    # Strip out times from all dates
    cfd_data = pd.DataFrame(
        np.array(cfd_data.values, dtype="<M8[ns]").astype("<M8[D]").astype("<M8[ns]"),
        columns=cfd_data.columns,
        index=cfd_data.index,
    )

    # Replace missing NaT values (happens if a status is skipped) with the subsequent timestamp
    cfd_data = cfd_data.fillna(method="bfill", axis=1)

    # Count number of times each date occurs, preserving column order
    cfd_data = pd.concat(
        {col: cfd_data[col].value_counts() for col in cfd_data}, axis=1
    )[cycle_names]

    # Fill missing dates with 0 and run a cumulative sum
    cfd_data = cfd_data.fillna(0).cumsum(axis=0).sort_index()

    # Reindex to make sure we have all dates
    start, end = cfd_data.index.min(), cfd_data.index.max()
    if start is not pd.NaT and end is not pd.NaT:
        cfd_data = cfd_data.reindex(pd.date_range(start, end, freq="D"), method="ffill")

    return cfd_data


# Quality - How Well - "Do it Right"
def defect_percentage(throughput: DataFrame, pbi_type: str) -> DataFrame:
    throughput = throughput.resample("W").sum()

    if pbi_type == "Total":
        total = throughput["Total"]
    elif pbi_type == "Bug":
        total = throughput["Bug"]
    else:
        try:
            total = throughput["Bug"] + throughput[pbi_type]
        except KeyError:
            total = throughput[pbi_type]

    if "Bug" in throughput:
        throughput["Defect Percentage"] = round((throughput["Bug"] / (total)), 2)
    else:
        throughput["Defect Percentage"] = throughput["Total"] * 0
    throughput = throughput.fillna(0)
    return throughput
