import pandas as pd

def throughput(cycle_data):
    # We need to pivot data since several values in the Done column will be nill or 0
    table=pd.pivot_table(cycle_data,values="Key",index=['Done'],columns="Type",aggfunc='count')
    throughput = pd.DataFrame(table.to_records())
    throughput["Week"] = throughput["Done"].dt.strftime('%Y-%U')
    throughput = throughput.rename({"Done":"Total"},axis=1)
    throughput = throughput.groupby("Week").count()
    return throughput
