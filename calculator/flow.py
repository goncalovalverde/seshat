import pandas as pd

# Productivity - How Much - "Do Lots"
def throughput(cycle_data):
    # Pivot data since several values in the Done column will be nil or 0
    table = pd.pivot_table(cycle_data, values="Key", index=['Done'], columns="Type",aggfunc='count')
    throughput = pd.DataFrame(table.to_records())
    throughput["Week"] = throughput["Done"].dt.strftime('%Y-%U')
    throughput = throughput.rename({"Done": "Total"}, axis=1)
    throughput = throughput.groupby("Week").count()
    return throughput


# Responsivness - How Fast - "Do it Fast"
def lead_time(cycle_data):
    cycle_data["Lead Time"] = cycle_data["Done"]-cycle_data["Created"]
    return cycle_data


# Predictability - How Repeatable - "Do it Predicably"
def net_flow(cycle_data):
    table_created = pd.pivot_table(
        cycle_data, values="Key",
        index=['Created'],
        columns="Type", aggfunc='count')
    table_done = pd.pivot_table(
        cycle_data, values="Key",
        index=['Done'],
        columns="Type", aggfunc='count')

    table = pd.merge(table_created,table_done,how="outer")
    print(table_created)
    print(table_done)
    print(table)
    net_flow = ''
    return net_flow


# Quality - How Well - "Do it Right"
def defect_percentage(throughput):
    throughput["Defect Percentage"] = round((throughput["Bug"]/(throughput["Total"]))*100,2)
    return throughput

