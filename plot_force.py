import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

file_id = 'mri_noise_floor'

df = pd.read_csv('log_'+file_id+'.csv')
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

Fs = 250.
Wn = 10.
Wn_rad = Wn/Fs*2

b,a = signal.butter(4, Wn_rad, 'lowpass')

y_0_filt = signal.lfilter(b,a,y_0_interp)

################
# FFT analysis #
################

Fs = 250.
y = y_0_filt
y = y-np.mean(y)
n = len(y) # length of the signal
k = np.arange(n)
T = n/Fs
frq = k/T # two sides frequency range
frq = frq[range(n/2)] # one side frequency range

Y = np.fft.fft(y)/n # fft computing and normalization
Y = Y[range(n/2)]

plt.plot(frq,abs(Y),'r') # plotting the spectrum
plt.xlabel('Freq (Hz)')
plt.ylabel('|Y(freq)|')
