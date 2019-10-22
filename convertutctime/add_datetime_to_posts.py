import pandas as pd
import time
from datetime import datetime
import numpy

def epoch_to_local(epoch_time):
    local_time = time.strftime('%Y-%m-%d %H:%M:%S %z', time.localtime(epoch_time))
    return local_time

posts = pd.read_csv("posts.csv")

#Example time coversion
utc_time_ex = posts["created_utc"][0]
print(type(utc_time_ex))
print(epoch_to_local(utc_time_ex))

local_time = []

for i in range(0,len(posts["created_utc"])):
    local = epoch_to_local(posts["created_utc"][i])
    local_time.append(local)

posts["local_datetime"] = local_time

posts.to_csv("posts_plus_datetime.csv", index=False)