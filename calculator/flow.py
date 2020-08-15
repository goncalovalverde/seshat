import pandas as pd


def throughput(cycle_data):
    # Pivot data since several values in the Done column will be nil or 0
    table = pd.pivot_table(cycle_data, values="Key", index=['Done'], columns="Type",aggfunc='count')
    throughput = pd.DataFrame(table.to_records())
    throughput["Week"] = throughput["Done"].dt.strftime('%Y-%U')
    throughput = throughput.rename({"Done": "Total"}, axis=1)
    throughput = throughput.groupby("Week").count()
    return throughput


def lead_time(cycle_data):
    cycle_data["Lead Time"] = cycle_data["Done"]-cycle_data["Created"]
    return cycle_data
