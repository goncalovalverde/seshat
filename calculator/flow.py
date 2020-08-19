import pandas as pd


# Productivity - How Much - "Do Lots"
def throughput(cycle_data):
    #throughput = count_items_in_week(cycle_data, "Done")
    throughput = group_by_date(cycle_data, "Done")
    return throughput


# Responsivness - How Fast - "Do it Fast"
def lead_time(cycle_data):
    cycle_data["Lead Time"] = cycle_data["Done"]-cycle_data["Created"]
    return cycle_data


# Predictability - How Repeatable - "Do it Predicably"
def net_flow(cycle_data):
    created = group_by_date(cycle_data, "Created")
    done = group_by_date(cycle_data, "Done")
    net_flow = pd.merge(created, done, left_index=True, right_index=True)
    net_flow["Net Flow"] = net_flow["Total_y"] - net_flow["Total_x"]
    return net_flow


# Quality - How Well - "Do it Right"
def defect_percentage(throughput):
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
    grouped_by_date = pd.DataFrame(table.to_records())
    grouped_by_date = grouped_by_date.fillna(0)
    grouped_by_date["Total"] = grouped_by_date.sum(axis=1)
    return grouped_by_date
