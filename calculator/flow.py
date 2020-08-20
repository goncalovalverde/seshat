import pandas as pd


# Productivity - How Much - "Do Lots"
def throughput(cycle_data):
    #throughput = count_items_in_week(cycle_data, "Done")
    throughput = group_by_date(cycle_data, "Done")
    throughput = throughput.set_index("Done")
    return throughput


# Responsivness - How Fast - "Do it Fast"
def lead_time(cycle_data):
    cycle_data["Lead Time"] = cycle_data["Done"]-cycle_data["Created"]
    cycle_data["Lead Time"] = pd.to_numeric(cycle_data["Lead Time"].dt.days, downcast='integer')
    return cycle_data


def avg_lead_time(cycle_data):
    lead_time = cycle_data[["Done","Lead Time"]].copy()
    lead_time = lead_time.groupby("Done").mean()
    # TODO: check if using mean here is correct
    lead_time = lead_time.resample("W").mean()
    return lead_time

# Predictability - How Repeatable - "Do it Predicably"
def net_flow(cycle_data):
    created = group_by_date(cycle_data, "Created")
    done = group_by_date(cycle_data, "Done")
    net_flow = pd.merge(created, done, left_index=True, right_index=True)
    net_flow["Net Flow"] = net_flow["Total_y"] - net_flow["Total_x"]
    net_flow = net_flow.set_index("Done")
    net_flow = net_flow.resample("W").sum()
    return net_flow


# Quality - How Well - "Do it Right"
def defect_percentage(throughput):
    throughput = throughput.resample("W").sum()
    throughput["Defect Percentage"] = round((throughput["Bug"]/(throughput["Total"]))*100,2)
    return throughput


# Auxiliary function to simplify counting total per week
def count_items_in_week(cycle_data, index):
    table = pd.pivot_table(cycle_data, values="Key", index=[index], columns="Type", aggfunc='count')
    item_count_in_week = pd.DataFrame(table.to_records())
    item_count_in_week["Date"] = item_count_in_week[index].dt.strftime('%Y-%U')
    item_count_in_week = item_count_in_week.rename({index: "Total"}, axis=1)
    item_count_in_week = item_count_in_week.groupby("Date").count()
    return item_count_in_week


def group_by_date(cycle_data, index):
    table = pd.pivot_table(cycle_data, values="Key", index=[index], columns="Type", aggfunc='count')
    df = pd.DataFrame(table.to_records())
    df = df.fillna(0)
    df["Total"] = df.sum(axis=1)
    return df
