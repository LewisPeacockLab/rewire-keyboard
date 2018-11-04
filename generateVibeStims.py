from scipy.io import wavfile
import numpy as np

SAMPLE_RATE = 44100.0 # Hz
MAX_AMPLITUDE = 32767.0 # 16 bit int

def generateStim(stim_name = 'demo', stim_offset=0.1,
        stim_duration=0.02, stim_frequency=250, volume=1):
    amplitude = volume*MAX_AMPLITUDE
    total_duration = stim_duration + np.abs(stim_offset)
    stim_data = np.zeros((int(total_duration*SAMPLE_RATE),2),dtype=np.int16)
    n_stim_points = int(stim_duration*SAMPLE_RATE)
    stim_time_vector = np.linspace(0, stim_duration, n_stim_points)
    stim_vector = np.array(amplitude*-np.cos(stim_frequency*2*np.pi*stim_time_vector),dtype=np.int16)
    if stim_offset >= 0:
        first_stim = 0
        second_stim = 1
    else:
        first_stim = 1
        second_stim = 0
    stim_data[:n_stim_points,first_stim] = stim_vector
    stim_data[-n_stim_points:,second_stim] = stim_vector
    wavfile.write(stim_name+'.WAV', int(SAMPLE_RATE), stim_data)

def generateMultiStim(timing_array = [.03, .07, .12, .18, .25, .4],
        stim_duration=.02, stim_frequency=250, volume=1):
    for idx, timing in enumerate(timing_array):
        stim_offset = timing_array[idx]
        stim_name = 'P'+str(idx)
        generateStim(stim_name, stim_offset, stim_duration, stim_frequency, volume)
        stim_offset = -timing_array[idx]
        stim_name = 'N'+str(idx)
        generateStim(stim_name, stim_offset, stim_duration, stim_frequency, volume)

