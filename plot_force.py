import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

file_id = '1545446890'

df = pd.read_csv('log_'+file_id+'.csv')
df = df[1:] # dropping first 'empty' frame
df['time'] = np.cumsum(df.time_passed)

start_time = 0
end_time = 5
frame_rate = 60.

t = np.arange(start_time, end_time, 1/frame_rate)

y_0 = df.force_0; y_1 = df.force_1; y_2 = df.force_2; y_3 = df.force_3

y_0_interp = np.interp(t, df.time, y_0)
y_1_interp = np.interp(t, df.time, y_1)
y_2_interp = np.interp(t, df.time, y_2)
y_3_interp = np.interp(t, df.time, y_3)

plt.ion()
plt.plot(t, y_0_interp)
plt.plot(t, y_1_interp)
plt.plot(t, y_2_interp)
plt.plot(t, y_3_interp)
