from logging import exception
import pandas as pd
import logging


def cycle_data(data, config):
    # get the first element of the workflow
    # to know where to start calculating the lead time
    workflow_keys = list(config["Workflow"].keys())
    start = workflow_keys[0]
    start = "Created"

    # adding lead time to cycle_data
    cycle_data = lead_time(data, start)

    # adding cycle_time (between workflow steps) to cycle_data
    for i in range(len(workflow_keys) - 1):
        start = workflow_keys[i]
        end = workflow_keys[i + 1]
        # adding cycle_time to cycle_data
        cycle_time(cycle_data, start, end)

    return cycle_data


# Productivity - How Much - "Do Lots"
def throughput(cycle_data):
    throughput = group_by_date(cycle_data, "Done")
    # throughput = throughput.set_index("Done")
    return throughput


def velocity(cycle_data):
    table = pd.pivot_table(
        cycle_data,
        values="Story Points",
        index=["Done"],
        columns="Type",
        fill_value=0,
        aggfunc="sum",
    )
    df = pd.DataFrame(table.to_records())
    df = df.resample("D", on="Done").sum()
    df["Total"] = df.sum(axis=1)
    return df


def story_points(cycle_data):
    table = pd.pivot_table(
        cycle_data,
        values="Key",
        index=["Done"],
        columns="Story Points",
        fill_value=0,
        aggfunc="count",
    )
    df = pd.DataFrame(table.to_records())
    df = df.resample("D", on="Done").sum()
    df["Total"] = df.sum(axis=1)
    return df


# Responsiveness - How Fast - "Do it Fast"
def lead_time(cycle_data, start):
    logging.debug("Calculating lead time for " + start)
    cycle_data["Lead Time"] = cycle_data["Done"] - cycle_data[start]
    cycle_data["Lead Time"] = pd.to_numeric(
        cycle_data["Lead Time"].dt.days, downcast="integer"
    )
    return cycle_data


# TODO: migrate this to multi header df (and apply it to all dataframe )
def cycle_time(cycle_data, start, end):
    logging.debug("Calculating cycle time for start:" + start + " and end:" + end)
    try:
        column = "Cycle Time " + start
        cycle_data[column] = cycle_data[end] - cycle_data[start]
        cycle_data[column] = pd.to_numeric(
            cycle_data[column].dt.days, downcast="integer"
        )
        return cycle_data
    except KeyError as e:
        logging.error("No data found for " + str(e))
        logging.error("Are you sure you configured your workflow correctly?")
        return cycle_data


def avg_lead_time(cycle_data, type):
    lead_time = cycle_data[["Done", "Type", "Lead Time"]].copy()

    if type != "Total":
        lead_time = lead_time.loc[lead_time["Type"] == type]

    lead_time = lead_time.groupby("Done").mean()

    # TODO: check if using mean here is correct
    lead_time = lead_time.resample("W").mean()
    lead_time = lead_time.fillna(0)
    return lead_time


# Predictability - How Repeatable - "Do it Predictably"
def net_flow(cycle_data, type):
    created = group_by_date(cycle_data, "Created")
    done = group_by_date(cycle_data, "Done")

    net_flow = pd.merge(created, done, left_index=True, right_index=True, how="outer")
    net_flow = net_flow.fillna(0)
    # Net Flow : Done items - Created items
    net_flow["Net Flow"] = net_flow[type + "_y"] - net_flow[type + "_x"]
    # WIP : Amount of items still in progress.
    # We calculate this using cumulative sum
    net_flow["WIP"] = net_flow[type + "_x"].cumsum() - net_flow[type + "_y"].cumsum()
    net_flow = net_flow.fillna(0)
    return net_flow


# Quality - How Well - "Do it Right"
def defect_percentage(throughput, type):
    throughput = throughput.resample("W").sum()

    if type == "Total":
        total = throughput["Total"]
    elif type == "Bug":
        total = throughput["Bug"]
    else:
        try:
            total = throughput["Bug"] + throughput[type]
        except KeyError:
            total = throughput[type]

    if "Bug" in throughput:
        throughput["Defect Percentage"] = round((throughput["Bug"] / (total)), 2)
    else:
        throughput["Defect Percentage"] = throughput["Total"] * 0
    throughput = throughput.fillna(0)
    return throughput


def group_by_date(cycle_data, index):
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
