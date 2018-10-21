from scipy.io import wavfile
import numpy as np

sample_rate = 44100.0 # Hz
max_value = 32767.0 # 16 bit int

def generateStim(stim_duration=0.02, stim_frequency=250, stim_offset=0.1, mode='stereo'):
    stim_name = str(int(1000*stim_offset))+'_'+str(int(stim_frequency))+'_'+str(int(1000*stim_duration))
    total_duration = stim_duration + np.abs(stim_offset)
    stim_data = np.zeros((int(total_duration*sample_rate),2),dtype=np.int16)
    n_stim_points = int(stim_duration*sample_rate)
    stim_time_vector = np.linspace(0, stim_duration, n_stim_points)
    stim_vector = np.array(max_value*-np.cos(stim_frequency*2*np.pi*stim_time_vector),dtype=np.int16)
    if stim_offset >= 0:
        first_stim = 0
        second_stim = 1
    else:
        first_stim = 1
        second_stim = 0
    stim_data[:n_stim_points,first_stim] = stim_vector
    stim_data[-n_stim_points:,second_stim] = stim_vector
    if mode == 'stereo':
        wavfile.write(stim_name+'.wav', int(sample_rate), stim_data)
    elif mode == 'mono':
        wavfile.write(stim_name+'_first.wav', int(sample_rate), stim_data[:,first_stim])
        wavfile.write(stim_name+'_second.wav', int(sample_rate), stim_data[:,second_stim])
    else:
        print 'invalid mode (please select mono or stereo)'
