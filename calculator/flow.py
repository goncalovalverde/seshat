import pandas as pd


# Productivity - How Much - "Do Lots"
def throughput(cycle_data):
    #throughput = count_items_in_week(cycle_data, "Done")
    throughput = group_by_date(cycle_data, "Done")
    throughput = throughput.set_index("Done")
    return throughput


# Responsivness - How Fast - "Do it Fast"
def lead_time(cycle_data, start):
    cycle_data["Lead Time"] = cycle_data["Done"]-cycle_data[start]
    cycle_data["Lead Time"] = pd.to_numeric(cycle_data["Lead Time"].dt.days, downcast='integer')
    return cycle_data


# TODO: migrate this to multi header df (and apply it to all dataframe )
def cycle_time(cycle_data, start, end):
    cycle_data["Cycle Time " + start] = cycle_data[end]-cycle_data[start]
    cycle_data["Cycle Time " + start] = pd.to_numeric(cycle_data["Cycle Time " + start].dt.days, downcast='integer')
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


# Predictability - How Repeatable - "Do it Predicably"
def net_flow(cycle_data, type):
    created = group_by_date(cycle_data, "Created")
    done = group_by_date(cycle_data, "Done")
    net_flow = pd.merge(created, done, left_index=True, right_index=True)
    net_flow["Net Flow"] = net_flow[type + "_y"] - net_flow[type + "_x"]
    net_flow = net_flow.set_index("Done")
    net_flow["WIP"] = net_flow[type + "_y"].cumsum() - net_flow[type + "_x"].cumsum()
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
        total = throughput["Bug"] + throughput[type]
   
    if "Bug" in throughput:
        throughput["Defect Percentage"] = round((throughput["Bug"]/(total))*100,2)
    else:
        throughput["Defect Percentage"] = throughput["Total"]*0
    throughput = throughput.fillna(0)
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
