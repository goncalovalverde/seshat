import pandas as pd

def throughput(cycle):
    table=pd.pivot_table(cycle,values="Key",index=['Done'],columns="Type",aggfunc='count')
    return table
