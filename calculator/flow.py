import pandas as pd


# Productivity - How Much - "Do Lots"
def throughput(cycle_data):
    throughput = count_items_in_week(cycle_data, "Done")
    return throughput


# Responsivness - How Fast - "Do it Fast"
def lead_time(cycle_data):
    cycle_data["Lead Time"] = cycle_data["Done"]-cycle_data["Created"]
    return cycle_data


# Predictability - How Repeatable - "Do it Predicably"
def net_flow(cycle_data):
    print(cycle_data)
    created = count_items_in_week(cycle_data, "Created")
    done = count_items_in_week(cycle_data, "Done")
    table = pd.merge(created, done, left_index=True, right_index=True)
    table["Net Flow"] = table["Total_y"] - table["Total_x"]
    return table


# Quality - How Well - "Do it Right"
def defect_percentage(throughput):
    throughput["Defect Percentage"] = round((throughput["Bug"]/(throughput["Total"]))*100,2)
    return throughput


# Auxiliary function to simplify counting total per week
def count_items_in_week(cycle_data, index):
    table = pd.pivot_table(cycle_data, values="Key", index=[index], columns="Type", aggfunc='count')
    item_count_in_week = pd.DataFrame(table.to_records())
    item_count_in_week["Week"] = item_count_in_week[index].dt.strftime('%Y-%U')
    item_count_in_week = item_count_in_week.rename({index: "Total"}, axis=1)
    item_count_in_week = item_count_in_week.groupby("Week").count()
    return item_count_in_week
