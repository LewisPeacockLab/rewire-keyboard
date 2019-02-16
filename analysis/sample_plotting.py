import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

file_id = '4_key_scanner_not_running'
file_id = '4_key_scanner_running_mb2'
file_id = '4_key_scanner_running_mb1'
file_id = '4_key_scanner_running_mb2_close'
file_id = '4_key_scanner_running_mb1_close'
file_id = '4_key_scanner_running_mb1_close'
file_id = 'test_capacitors_smaller'
file_id = '3p33hz_press'

df = pd.read_csv('log_'+file_id+'.txt')
df['time'] = np.cumsum(df.time_passed)

start_time = np.min(df.time)
end_time = np.max(df.time)
frame_rate = 250. #60.

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

####################
# signal filtering #
####################
from scipy import signal

filter_bool = True

if filter_bool:
    Fs = 250.
    Wn = 10.
    Wn_rad = Wn/Fs*2

    b,a = signal.butter(3, Wn_rad, 'lowpass')

    y_0_filt = signal.lfilter(b,a,y_0_interp)
else:
    y_0_filt = y_0_interp

################
# FFT analysis #
################

Fs = 250.
# y = y_0_filt
y = y_1_interp
y = y-np.mean(y)
n = len(y) # length of the signal
k = np.arange(n)
T = n/Fs
frq = k/T # two sides frequency range
frq = frq[range(n/2)] # one side frequency range

Y = np.fft.fft(y)/n # fft computing and normalization
Y = Y[range(n/2)]

plt.plot(frq,abs(Y),'b') # plotting the spectrum
plt.xlabel('Freq (Hz)')
plt.ylabel('|Y(freq)|')
# plt.ylim((0,0.05))
plt.ylim((0,5e-4))

######################
# noise correlations #
######################
import seaborn as sea
vmin = 0
vmax = 1

sea.heatmap(np.corrcoef([y_0_interp, y_1_interp, y_2_interp, y_3_interp]),
    vmin=vmin, vmax=vmax)
plt.title('corr b/w forces: end of scanner bore')

#######################
# comparing filtering #
#######################

file_id_1 = '4_key_scanner_not_running'
file_id_2 = '4_key_scanner_running_mb2'
file_id_3 = '4_key_scanner_running_mb2_close'

df1 = pd.read_csv('log_'+file_id_1+'.txt')
df1['time'] = np.cumsum(df1.time_passed)
df2 = pd.read_csv('log_'+file_id_2+'.txt')
df2['time'] = np.cumsum(df1.time_passed)
df3 = pd.read_csv('log_'+file_id_3+'.txt')
df3['time'] = np.cumsum(df3.time_passed)

start_time = 0 #np.min(df.time)
end_time = 50 #np.max(df.time)
frame_rate = 250. #60.

t = np.arange(start_time, end_time, 1/frame_rate)

y1 = df1.force_1
y2 = df2.force_1
y3 = df3.force_1

y_1_interp = np.interp(t, df1.time, y1)
y_2_interp = np.interp(t, df2.time, y2)
y_3_interp = np.interp(t, df3.time, y3)

filter_bool = False

if filter_bool:
    Fs = 250.
    Wn = 10.
    Wn_rad = Wn/Fs*2

    b,a = signal.butter(3, Wn_rad, 'lowpass')

    y_1_filt = signal.lfilter(b,a,y_1_interp)
    y_2_filt = signal.lfilter(b,a,y_2_interp)
    y_3_filt = signal.lfilter(b,a,y_3_interp)
else:
    y_1_filt = y_1_interp
    y_2_filt = y_2_interp
    y_3_filt = y_3_interp

plt.ion()
plt.plot(t, y_3_filt)
plt.plot(t, y_2_filt)
plt.plot(t, y_1_filt)
plt.title('unfiltered force data')
plt.legend(['center bore','end of bore','idle'])
plt.ylim([0.35,0.5])
plt.xlim([1,50])
