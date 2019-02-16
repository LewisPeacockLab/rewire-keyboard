import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

OUT_DIR = '/Users/efun/Dropbox/code/rewire-keyboard/icorr-2019/'
COLORS = ['tab:red','tab:orange','tab:blue','k']

def load_dataset(file_id, frame_rate=250., start_time=0, end_time=0,
        channel_names=['y0','y1','y2','y3']):
    df = pd.read_csv(file_id+'.txt')
    df['time'] = np.cumsum(df.time_passed)

    if end_time == 0:
        end_time = np.max(df.time)-np.min(df.time)

    t = np.arange(start_time, end_time, 1/frame_rate)

    y_0 = df.force_0; y_1 = df.force_1; y_2 = df.force_2; y_3 = df.force_3

    y_0_interp = np.interp(t, df.time, y_0)
    y_1_interp = np.interp(t, df.time, y_1)
    y_2_interp = np.interp(t, df.time, y_2)
    y_3_interp = np.interp(t, df.time, y_3)

    t = t-start_time # reset time to start from 0

    new_df = pd.DataFrame({'t':t,
        channel_names[0]:y_0_interp,
        channel_names[1]:y_1_interp,
        channel_names[2]:y_2_interp,
        channel_names[3]:y_3_interp})
    return new_df

def psd_analysis(y, Fs=250., window='hanning', nperseg=256):
    f, Pxx = signal.welch(y, Fs, window, nperseg)
    return f, Pxx
    # plt.semilogy(f, Pxx)

def filter_ts(y, Fs=250., Wn=10., order=1):
    Wn_rad = Wn/Fs*2
    b,a = signal.butter(order, Wn_rad, 'lowpass')
    y_filt = signal.lfilter(b,a,y)
    return y_filt

##########################
# FILTERING: SCANNER OFF #
##########################

def plot_filtering_scanner_off(savefig=False):
    # frequency digital
    # digital_noise_df = load_dataset('../logs/log_4_key_scanner_not_running')
    digital_noise_df = load_dataset('../logs/log_5min_baseline_nofilter')
    # digital_noise_df = load_dataset('../logs/log_5min_baseline_analog_new')
    noise_y_unfilt = digital_noise_df.y3
    noise_t = digital_noise_df.t
    noise_y_unfilt = noise_y_unfilt-np.mean(noise_y_unfilt)
    cutoff_freqs = [100,30,10] # in Hz
    noise_y_filt_1 = filter_ts(noise_y_unfilt, Wn=cutoff_freqs[0])
    noise_y_filt_2 = filter_ts(noise_y_unfilt, Wn=cutoff_freqs[1])
    noise_y_filt_3 = filter_ts(noise_y_unfilt, Wn=cutoff_freqs[2])
    print 'unfiltered: '+str(np.std(signal.detrend(noise_y_unfilt)))
    print '100hz: '+str(np.std(signal.detrend(noise_y_filt_1)))
    print '30hz: '+str(np.std(signal.detrend(noise_y_filt_2)))
    print '10hz: '+str(np.std(signal.detrend(noise_y_filt_3)))
    # noise_y_filt_1 = digital_noise_df.y2-np.mean(digital_noise_df.y2)
    # noise_y_filt_2 = digital_noise_df.y1-np.mean(digital_noise_df.y1)
    # noise_y_filt_3 = digital_noise_df.y0-np.mean(digital_noise_df.y0)
    f,wxx_0 = psd_analysis(noise_y_unfilt)
    f,wxx_1 = psd_analysis(noise_y_filt_1)
    f,wxx_2 = psd_analysis(noise_y_filt_2)
    f,wxx_3 = psd_analysis(noise_y_filt_3)
    plt.ion()
    ax1 = plt.subplot(2,2,3)
    plt.semilogy(f,wxx_3, color=COLORS[0])
    plt.semilogy(f,wxx_2, color=COLORS[1])
    plt.semilogy(f,wxx_1, color=COLORS[2])
    plt.semilogy(f,wxx_0, color=COLORS[3])
    plt.xlim(0,100)
    plt.ylim((1e-11,1e-6))
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Power (N$^2$/Hz)')
    ax1.spines['right'].set_visible(False)
    ax1.spines['top'].set_visible(False)
    plt.legend(['10Hz low-pass','30Hz low-pass','100Hz low-pass','Unfiltered'], fontsize=8)

    # time series digital
    plot_offset = 0.01
    end_time = 0.5
    plot_end_idx = np.where(noise_t==end_time)[0][0]+1
    noise_t_trunc = noise_t[0:plot_end_idx]
    noise_y_unfilt_trunc = noise_y_unfilt[0:plot_end_idx]
    noise_y_filt_1_trunc = noise_y_filt_1[0:plot_end_idx]
    noise_y_filt_2_trunc = noise_y_filt_2[0:plot_end_idx]
    noise_y_filt_3_trunc = noise_y_filt_3[0:plot_end_idx]
    plt.ion()
    ax2 = plt.subplot(2,2,1)
    plt.plot(noise_t_trunc, noise_y_filt_3_trunc+3*plot_offset, color=COLORS[0])
    plt.plot(noise_t_trunc, noise_y_filt_2_trunc+2*plot_offset, color=COLORS[1])
    plt.plot(noise_t_trunc, noise_y_filt_1_trunc+1*plot_offset, color=COLORS[2])
    plt.plot(noise_t_trunc, noise_y_unfilt_trunc, color=COLORS[3])
    plt.xlim((0,end_time))
    plot_y_padding = 0.0025
    plt.ylim((-plot_offset,4*plot_offset))
    # plt.yticks([0,0.01])
    plt.title('(A) Digital filtering')
    plt.xlabel('Time (sec)')
    plt.ylabel('Force (N)')
    ax2.spines['right'].set_visible(False)
    ax2.spines['top'].set_visible(False)

    # frequency analog 
    analog_noise_df = load_dataset('../logs/log_5min_baseline_analog')
    noise_y_unfilt = analog_noise_df.y3
    noise_t = analog_noise_df.t
    noise_y_unfilt = noise_y_unfilt-np.mean(noise_y_unfilt)
    cutoff_freqs = [100,30,10] # in Hz
    noise_y_filt_1 = analog_noise_df.y2-np.mean(analog_noise_df.y2)
    noise_y_filt_2 = analog_noise_df.y1-np.mean(analog_noise_df.y1)
    noise_y_filt_3 = analog_noise_df.y0-np.mean(analog_noise_df.y0)
    print 'unfiltered: '+str(np.std(signal.detrend(noise_y_unfilt)))
    print '100hz: '+str(np.std(signal.detrend(noise_y_filt_1)))
    print '30hz: '+str(np.std(signal.detrend(noise_y_filt_2)))
    print '10hz: '+str(np.std(signal.detrend(noise_y_filt_3)))
    f,wxx_0 = psd_analysis(noise_y_unfilt)
    f,wxx_1 = psd_analysis(noise_y_filt_1)
    f,wxx_2 = psd_analysis(noise_y_filt_2)
    f,wxx_3 = psd_analysis(noise_y_filt_3)
    plt.ion()
    ax3 = plt.subplot(2,2,4)
    plt.semilogy(f,wxx_3, color=COLORS[0])
    plt.semilogy(f,wxx_2, color=COLORS[1])
    plt.semilogy(f,wxx_1, color=COLORS[2])
    plt.semilogy(f,wxx_0, color=COLORS[3])
    plt.xlim(0,100)
    plt.ylim((1e-11,1e-6))
    # plt.xlabel('Frequency (Hz)')
    # plt.ylabel('Power (N$^2$/Hz)')
    ax3.set_yticklabels([])
    ax3.spines['right'].set_visible(False)
    ax3.spines['top'].set_visible(False)

    # time series analog 
    plot_offset = 0.01
    start_time = 100 
    duration = 0.5
    end_time = start_time+duration
    plot_start_idx = np.where(noise_t==start_time)[0][0]
    plot_end_idx = np.where(noise_t==end_time)[0][0]+1
    noise_t_trunc = noise_t[0:(plot_end_idx-plot_start_idx)]
    noise_y_unfilt_trunc = noise_y_unfilt[plot_start_idx:plot_end_idx]
    noise_y_filt_1_trunc = noise_y_filt_1[plot_start_idx:plot_end_idx]
    noise_y_filt_2_trunc = noise_y_filt_2[plot_start_idx:plot_end_idx]
    noise_y_filt_3_trunc = noise_y_filt_3[plot_start_idx:plot_end_idx]
    plt.ion()
    ax4 = plt.subplot(2,2,2)
    plt.plot(noise_t_trunc, noise_y_filt_3_trunc+3*plot_offset, color=COLORS[0])
    plt.plot(noise_t_trunc, noise_y_filt_2_trunc+2*plot_offset, color=COLORS[1])
    plt.plot(noise_t_trunc, noise_y_filt_1_trunc+1*plot_offset, color=COLORS[2])
    plt.plot(noise_t_trunc, noise_y_unfilt_trunc, color=COLORS[3])
    plt.xlim((0,end_time-start_time))
    plot_y_padding = 0.0025
    plt.ylim((-plot_offset,4*plot_offset))
    # plt.yticks([])
    # plt.xlabel('Time (sec)')
    # plt.ylabel('Force (N)')
    plt.title('(B) Analog filtering')
    ax4.set_yticklabels([])
    ax4.spines['right'].set_visible(False)
    ax4.spines['top'].set_visible(False)

    # set figure size and save
    fig = plt.gcf()
    fig.set_size_inches(5, 3.5)
    plt.tight_layout(pad=0.25, h_pad=-0.5, w_pad=0.5)
    if savefig:
        fig.savefig(OUT_DIR+'fig-scanner-idle.png', dpi=450)

def plot_digital_filtering_scanner_on(savefig=False):
    # multiband 1 
    digital_noise_df = load_dataset('../logs/log_5min_scanner_far_sb_new')
    noise_y_unfilt = digital_noise_df.y3
    noise_t = digital_noise_df.t
    noise_y_unfilt = noise_y_unfilt-np.mean(noise_y_unfilt)
    cutoff_freqs = [100,30,10] # in Hz
    noise_y_filt_1 = filter_ts(noise_y_unfilt, Wn=cutoff_freqs[0])
    noise_y_filt_2 = filter_ts(noise_y_unfilt, Wn=cutoff_freqs[1])
    noise_y_filt_3 = filter_ts(noise_y_unfilt, Wn=cutoff_freqs[2])
    print 'unfiltered: '+str(np.std(signal.detrend(noise_y_unfilt)))
    print '100hz: '+str(np.std(signal.detrend(noise_y_filt_1)))
    print '30hz: '+str(np.std(signal.detrend(noise_y_filt_2)))
    print '10hz: '+str(np.std(signal.detrend(noise_y_filt_3)))
    f,wxx_0 = psd_analysis(noise_y_unfilt)
    f,wxx_1 = psd_analysis(noise_y_filt_1)
    f,wxx_2 = psd_analysis(noise_y_filt_2)
    f,wxx_3 = psd_analysis(noise_y_filt_3)
    plt.ion()
    ax1 = plt.subplot(2,2,3)
    plt.semilogy(f,wxx_3, color=COLORS[0])
    plt.semilogy(f,wxx_2, color=COLORS[1])
    plt.semilogy(f,wxx_1, color=COLORS[2])
    plt.semilogy(f,wxx_0, color=COLORS[3])
    plt.xlim(0,100)
    plt.ylim((1e-11,0.5*1e-5))
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Power (N$^2$/Hz)')
    ax1.spines['right'].set_visible(False)
    ax1.spines['top'].set_visible(False)
    plt.legend(['10Hz low-pass','30Hz low-pass','100Hz low-pass','Unfiltered'], fontsize=8)

    # multiband 1
    plot_offset = 0.01
    end_time = 0.5
    plot_end_idx = np.where(noise_t==end_time)[0][0]+1
    noise_t_trunc = noise_t[0:plot_end_idx]
    noise_y_unfilt_trunc = noise_y_unfilt[0:plot_end_idx]
    noise_y_filt_1_trunc = noise_y_filt_1[0:plot_end_idx]
    noise_y_filt_2_trunc = noise_y_filt_2[0:plot_end_idx]
    noise_y_filt_3_trunc = noise_y_filt_3[0:plot_end_idx]
    plt.ion()
    ax2 = plt.subplot(2,2,1)
    plt.plot(noise_t_trunc, noise_y_filt_3_trunc+3*plot_offset, color=COLORS[0])
    plt.plot(noise_t_trunc, noise_y_filt_2_trunc+2*plot_offset, color=COLORS[1])
    plt.plot(noise_t_trunc, noise_y_filt_1_trunc+1*plot_offset, color=COLORS[2])
    plt.plot(noise_t_trunc, noise_y_unfilt_trunc, color=COLORS[3])
    plt.xlim((0,end_time))
    plot_y_padding = 0.0025
    plt.ylim((-plot_offset,4*plot_offset))
    # plt.yticks([0,0.01])
    plt.title('(A) Singleband (end)')
    plt.xlabel('Time (sec)')
    plt.ylabel('Force (N)')
    ax2.spines['right'].set_visible(False)
    ax2.spines['top'].set_visible(False)

    # multiband 2
    digital_noise_df = load_dataset('../logs/log_5min_scanner_far_mb_new')
    noise_y_unfilt = digital_noise_df.y3
    noise_t = digital_noise_df.t
    noise_y_unfilt = noise_y_unfilt-np.mean(noise_y_unfilt)
    cutoff_freqs = [100,30,10] # in Hz
    noise_y_filt_1 = filter_ts(noise_y_unfilt, Wn=cutoff_freqs[0])
    noise_y_filt_2 = filter_ts(noise_y_unfilt, Wn=cutoff_freqs[1])
    noise_y_filt_3 = filter_ts(noise_y_unfilt, Wn=cutoff_freqs[2])
    print 'unfiltered: '+str(np.std(signal.detrend(noise_y_unfilt)))
    print '100hz: '+str(np.std(signal.detrend(noise_y_filt_1)))
    print '30hz: '+str(np.std(signal.detrend(noise_y_filt_2)))
    print '10hz: '+str(np.std(signal.detrend(noise_y_filt_3)))
    f,wxx_0 = psd_analysis(noise_y_unfilt)
    f,wxx_1 = psd_analysis(noise_y_filt_1)
    f,wxx_2 = psd_analysis(noise_y_filt_2)
    f,wxx_3 = psd_analysis(noise_y_filt_3)
    plt.ion()
    ax3 = plt.subplot(2,2,4)
    plt.semilogy(f,wxx_3, color=COLORS[0])
    plt.semilogy(f,wxx_2, color=COLORS[1])
    plt.semilogy(f,wxx_1, color=COLORS[2])
    plt.semilogy(f,wxx_0, color=COLORS[3])
    plt.xlim(0,100)
    plt.ylim((1e-11,0.5*1e-5))
    # plt.xlabel('Frequency (Hz)')
    # plt.ylabel('Power (N$^2$/Hz)')
    ax3.set_yticklabels([])
    ax3.spines['right'].set_visible(False)
    ax3.spines['top'].set_visible(False)

    # multiband 2
    plot_offset = 0.01
    end_time = 0.5
    plot_end_idx = np.where(noise_t==end_time)[0][0]+1
    noise_t_trunc = noise_t[0:plot_end_idx]
    noise_y_unfilt_trunc = noise_y_unfilt[0:plot_end_idx]
    noise_y_filt_1_trunc = noise_y_filt_1[0:plot_end_idx]
    noise_y_filt_2_trunc = noise_y_filt_2[0:plot_end_idx]
    noise_y_filt_3_trunc = noise_y_filt_3[0:plot_end_idx]
    plt.ion()
    ax4 = plt.subplot(2,2,2)
    plt.plot(noise_t_trunc, noise_y_filt_3_trunc+3*plot_offset, color=COLORS[0])
    plt.plot(noise_t_trunc, noise_y_filt_2_trunc+2*plot_offset, color=COLORS[1])
    plt.plot(noise_t_trunc, noise_y_filt_1_trunc+1*plot_offset, color=COLORS[2])
    plt.plot(noise_t_trunc, noise_y_unfilt_trunc, color=COLORS[3])
    plt.xlim((0,end_time))
    plot_y_padding = 0.0025
    plt.ylim((-plot_offset,4*plot_offset))
    # plt.yticks([])
    # plt.xlabel('Time (sec)')
    # plt.ylabel('Force (N)')
    plt.title('(B) Multiband (end)')
    ax4.set_yticklabels([])
    ax4.spines['right'].set_visible(False)
    ax4.spines['top'].set_visible(False)

    # set figure size and save
    fig = plt.gcf()
    fig.set_size_inches(5, 3.5)
    plt.tight_layout(pad=0.25, h_pad=-0.5, w_pad=0.5)
    if savefig:
        fig.savefig(OUT_DIR+'fig-scanner-running-digital.png', dpi=450) 


def plot_digital_filtering_scanner_on_close(savefig=False):
    # multiband 1 
    digital_noise_df = load_dataset('../logs/log_5min_scanner_close_sb_new')
    noise_y_unfilt = digital_noise_df.y3
    noise_t = digital_noise_df.t
    noise_y_unfilt = noise_y_unfilt-np.mean(noise_y_unfilt)
    cutoff_freqs = [100,30,10] # in Hz
    noise_y_filt_1 = filter_ts(noise_y_unfilt, Wn=cutoff_freqs[0])
    noise_y_filt_2 = filter_ts(noise_y_unfilt, Wn=cutoff_freqs[1])
    noise_y_filt_3 = filter_ts(noise_y_unfilt, Wn=cutoff_freqs[2])
    print 'unfiltered: '+str(np.std(signal.detrend(noise_y_unfilt)))
    print '100hz: '+str(np.std(signal.detrend(noise_y_filt_1)))
    print '30hz: '+str(np.std(signal.detrend(noise_y_filt_2)))
    print '10hz: '+str(np.std(signal.detrend(noise_y_filt_3)))
    f,wxx_0 = psd_analysis(noise_y_unfilt)
    f,wxx_1 = psd_analysis(noise_y_filt_1)
    f,wxx_2 = psd_analysis(noise_y_filt_2)
    f,wxx_3 = psd_analysis(noise_y_filt_3)
    plt.ion()
    ax1 = plt.subplot(2,2,3)
    plt.semilogy(f,wxx_3, color=COLORS[0])
    plt.semilogy(f,wxx_2, color=COLORS[1])
    plt.semilogy(f,wxx_1, color=COLORS[2])
    plt.semilogy(f,wxx_0, color=COLORS[3])
    plt.xlim(0,100)
    plt.ylim((1e-11,.5*1e-5))
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Power (N$^2$/Hz)')
    ax1.spines['right'].set_visible(False)
    ax1.spines['top'].set_visible(False)
    plt.legend(['10Hz low-pass','30Hz low-pass','100Hz low-pass','Unfiltered'], fontsize=8)

    # multiband 1
    plot_offset = 0.03
    end_time = 0.5
    plot_end_idx = np.where(noise_t==end_time)[0][0]+1
    noise_t_trunc = noise_t[0:plot_end_idx]
    noise_y_unfilt_trunc = noise_y_unfilt[0:plot_end_idx]
    noise_y_filt_1_trunc = noise_y_filt_1[0:plot_end_idx]
    noise_y_filt_2_trunc = noise_y_filt_2[0:plot_end_idx]
    noise_y_filt_3_trunc = noise_y_filt_3[0:plot_end_idx]
    plt.ion()
    ax2 = plt.subplot(2,2,1)
    plt.plot(noise_t_trunc, noise_y_filt_3_trunc+3*plot_offset, color=COLORS[0])
    plt.plot(noise_t_trunc, noise_y_filt_2_trunc+2*plot_offset, color=COLORS[1])
    plt.plot(noise_t_trunc, noise_y_filt_1_trunc+1*plot_offset, color=COLORS[2])
    plt.plot(noise_t_trunc, noise_y_unfilt_trunc, color=COLORS[3])
    plt.xlim((0,end_time))
    plot_y_padding = 0.0025
    plt.ylim((-plot_offset,4*plot_offset))
    # plt.yticks([0,0.1])
    plt.title('(A) Singleband (center)')
    plt.xlabel('Time (sec)')
    plt.ylabel('Force (N)')
    ax2.spines['right'].set_visible(False)
    ax2.spines['top'].set_visible(False)

    # multiband 2
    digital_noise_df = load_dataset('../logs/log_5min_scanner_close_mb_new')
    noise_y_unfilt = digital_noise_df.y3
    noise_t = digital_noise_df.t
    noise_y_unfilt = noise_y_unfilt-np.mean(noise_y_unfilt)
    cutoff_freqs = [100,30,10] # in Hz
    noise_y_filt_1 = filter_ts(noise_y_unfilt, Wn=cutoff_freqs[0])
    noise_y_filt_2 = filter_ts(noise_y_unfilt, Wn=cutoff_freqs[1])
    noise_y_filt_3 = filter_ts(noise_y_unfilt, Wn=cutoff_freqs[2])
    print 'unfiltered: '+str(np.std(signal.detrend(noise_y_unfilt)))
    print '100hz: '+str(np.std(signal.detrend(noise_y_filt_1)))
    print '30hz: '+str(np.std(signal.detrend(noise_y_filt_2)))
    print '10hz: '+str(np.std(signal.detrend(noise_y_filt_3)))
    f,wxx_0 = psd_analysis(noise_y_unfilt)
    f,wxx_1 = psd_analysis(noise_y_filt_1)
    f,wxx_2 = psd_analysis(noise_y_filt_2)
    f,wxx_3 = psd_analysis(noise_y_filt_3)
    plt.ion()
    ax3 = plt.subplot(2,2,4)
    plt.semilogy(f,wxx_3, color=COLORS[0])
    plt.semilogy(f,wxx_2, color=COLORS[1])
    plt.semilogy(f,wxx_1, color=COLORS[2])
    plt.semilogy(f,wxx_0, color=COLORS[3])
    plt.xlim(0,100)
    plt.ylim((1e-11,.5*1e-5))
    # plt.xlabel('Frequency (Hz)')
    # plt.ylabel('Power (N$^2$/Hz)')
    ax3.set_yticklabels([])
    ax3.spines['right'].set_visible(False)
    ax3.spines['top'].set_visible(False)

    # multiband 2
    plot_offset = 0.03
    end_time = 0.5
    plot_end_idx = np.where(noise_t==end_time)[0][0]+1
    noise_t_trunc = noise_t[0:plot_end_idx]
    noise_y_unfilt_trunc = noise_y_unfilt[0:plot_end_idx]
    noise_y_filt_1_trunc = noise_y_filt_1[0:plot_end_idx]
    noise_y_filt_2_trunc = noise_y_filt_2[0:plot_end_idx]
    noise_y_filt_3_trunc = noise_y_filt_3[0:plot_end_idx]
    plt.ion()
    ax4 = plt.subplot(2,2,2)
    plt.plot(noise_t_trunc, noise_y_filt_3_trunc+3*plot_offset, color=COLORS[0])
    plt.plot(noise_t_trunc, noise_y_filt_2_trunc+2*plot_offset, color=COLORS[1])
    plt.plot(noise_t_trunc, noise_y_filt_1_trunc+1*plot_offset, color=COLORS[2])
    plt.plot(noise_t_trunc, noise_y_unfilt_trunc, color=COLORS[3])
    plt.xlim((0,end_time))
    plot_y_padding = 0.0025
    plt.ylim((-plot_offset,4*plot_offset))
    # plt.yticks([])
    # plt.xlabel('Time (sec)')
    # plt.ylabel('Force (N)')
    plt.title('(B) Multiband (center)')
    ax4.set_yticklabels([])
    ax4.spines['right'].set_visible(False)
    ax4.spines['top'].set_visible(False)

    # set figure size and save
    fig = plt.gcf()
    fig.set_size_inches(5, 3.5)
    plt.tight_layout(pad=0.25, h_pad=-0.5, w_pad=0.5)
    if savefig:
        fig.savefig(OUT_DIR+'fig-scanner-running-digital-close.png', dpi=450) 


# def plot_digital_filtering_scanner_on(savefig=False):
def plot_analog_filtering_scanner_on(savefig=False):
    # multiband 1 
    digital_noise_df = load_dataset('../logs/log_5min_scanner_far_sb_new')
    noise_y_unfilt = digital_noise_df.y3
    noise_t = digital_noise_df.t
    noise_y_unfilt = noise_y_unfilt-np.mean(noise_y_unfilt)
    cutoff_freqs = [100,30,10] # in Hz
    noise_y_filt_1 = digital_noise_df.y2-np.mean(digital_noise_df.y2)
    noise_y_filt_2 = digital_noise_df.y1-np.mean(digital_noise_df.y1)
    noise_y_filt_3 = digital_noise_df.y0-np.mean(digital_noise_df.y0)
    print 'unfiltered: '+str(np.std(signal.detrend(noise_y_unfilt)))
    print '100hz: '+str(np.std(signal.detrend(noise_y_filt_1)))
    print '30hz: '+str(np.std(signal.detrend(noise_y_filt_2)))
    print '10hz: '+str(np.std(signal.detrend(noise_y_filt_3)))
    f,wxx_0 = psd_analysis(noise_y_unfilt)
    f,wxx_1 = psd_analysis(noise_y_filt_1)
    f,wxx_2 = psd_analysis(noise_y_filt_2)
    f,wxx_3 = psd_analysis(noise_y_filt_3)
    plt.ion()
    ax1 = plt.subplot(2,2,3)
    plt.semilogy(f,wxx_3, color=COLORS[0])
    plt.semilogy(f,wxx_2, color=COLORS[1])
    plt.semilogy(f,wxx_1, color=COLORS[2])
    plt.semilogy(f,wxx_0, color=COLORS[3])
    plt.xlim(0,100)
    plt.ylim((1e-11,0.5*1e-5))
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Power (N$^2$/Hz)')
    ax1.spines['right'].set_visible(False)
    ax1.spines['top'].set_visible(False)
    plt.legend(['10Hz low-pass','30Hz low-pass','100Hz low-pass','Unfiltered'], fontsize=8)

    # multiband 1
    plot_offset = 0.01
    end_time = 0.5
    plot_end_idx = np.where(noise_t==end_time)[0][0]+1
    noise_t_trunc = noise_t[0:plot_end_idx]
    noise_y_unfilt_trunc = noise_y_unfilt[0:plot_end_idx]
    noise_y_filt_1_trunc = noise_y_filt_1[0:plot_end_idx]
    noise_y_filt_2_trunc = noise_y_filt_2[0:plot_end_idx]
    noise_y_filt_3_trunc = noise_y_filt_3[0:plot_end_idx]
    plt.ion()
    ax2 = plt.subplot(2,2,1)
    plt.plot(noise_t_trunc, noise_y_filt_3_trunc+3*plot_offset, color=COLORS[0])
    plt.plot(noise_t_trunc, noise_y_filt_2_trunc+2*plot_offset, color=COLORS[1])
    plt.plot(noise_t_trunc, noise_y_filt_1_trunc+1*plot_offset, color=COLORS[2])
    plt.plot(noise_t_trunc, noise_y_unfilt_trunc, color=COLORS[3])
    plt.xlim((0,end_time))
    plot_y_padding = 0.0025
    plt.ylim((-plot_offset,4*plot_offset))
    # plt.yticks([0,0.01])
    plt.title('(A) Singleband (end)')
    plt.xlabel('Time (sec)')
    plt.ylabel('Force (N)')
    ax2.spines['right'].set_visible(False)
    ax2.spines['top'].set_visible(False)

    # multiband 2
    digital_noise_df = load_dataset('../logs/log_5min_scanner_far_mb_new')
    # noise_y_unfilt = digital_noise_df.y0
    noise_y_unfilt = digital_noise_df.y3
    noise_t = digital_noise_df.t
    noise_y_unfilt = noise_y_unfilt-np.mean(noise_y_unfilt)
    cutoff_freqs = [100,30,10] # in Hz
    # noise_y_filt_1 = filter_ts(noise_y_unfilt, Wn=cutoff_freqs[0])
    # noise_y_filt_2 = filter_ts(noise_y_unfilt, Wn=cutoff_freqs[1])
    # noise_y_filt_3 = filter_ts(noise_y_unfilt, Wn=cutoff_freqs[2])
    noise_y_filt_1 = digital_noise_df.y2-np.mean(digital_noise_df.y2)
    noise_y_filt_2 = digital_noise_df.y1-np.mean(digital_noise_df.y1)
    noise_y_filt_3 = digital_noise_df.y0-np.mean(digital_noise_df.y0)
    print 'unfiltered: '+str(np.std(signal.detrend(noise_y_unfilt)))
    print '100hz: '+str(np.std(signal.detrend(noise_y_filt_1)))
    print '30hz: '+str(np.std(signal.detrend(noise_y_filt_2)))
    print '10hz: '+str(np.std(signal.detrend(noise_y_filt_3)))
    f,wxx_0 = psd_analysis(noise_y_unfilt)
    f,wxx_1 = psd_analysis(noise_y_filt_1)
    f,wxx_2 = psd_analysis(noise_y_filt_2)
    f,wxx_3 = psd_analysis(noise_y_filt_3)
    plt.ion()
    ax3 = plt.subplot(2,2,4)
    plt.semilogy(f,wxx_3, color=COLORS[0])
    plt.semilogy(f,wxx_2, color=COLORS[1])
    plt.semilogy(f,wxx_1, color=COLORS[2])
    plt.semilogy(f,wxx_0, color=COLORS[3])
    plt.xlim(0,100)
    plt.ylim((1e-11,0.5*1e-5))
    # plt.xlabel('Frequency (Hz)')
    # plt.ylabel('Power (N$^2$/Hz)')
    ax3.set_yticklabels([])
    ax3.spines['right'].set_visible(False)
    ax3.spines['top'].set_visible(False)

    # multiband 2
    plot_offset = 0.01
    end_time = 0.5
    plot_end_idx = np.where(noise_t==end_time)[0][0]+1
    noise_t_trunc = noise_t[0:plot_end_idx]
    noise_y_unfilt_trunc = noise_y_unfilt[0:plot_end_idx]
    noise_y_filt_1_trunc = noise_y_filt_1[0:plot_end_idx]
    noise_y_filt_2_trunc = noise_y_filt_2[0:plot_end_idx]
    noise_y_filt_3_trunc = noise_y_filt_3[0:plot_end_idx]
    plt.ion()
    ax4 = plt.subplot(2,2,2)
    plt.plot(noise_t_trunc, noise_y_filt_3_trunc+3*plot_offset, color=COLORS[0])
    plt.plot(noise_t_trunc, noise_y_filt_2_trunc+2*plot_offset, color=COLORS[1])
    plt.plot(noise_t_trunc, noise_y_filt_1_trunc+1*plot_offset, color=COLORS[2])
    plt.plot(noise_t_trunc, noise_y_unfilt_trunc, color=COLORS[3])
    plt.xlim((0,end_time))
    plot_y_padding = 0.0025
    plt.ylim((-plot_offset,4*plot_offset))
    # plt.yticks([])
    # plt.xlabel('Time (sec)')
    # plt.ylabel('Force (N)')
    plt.title('(B) Multiband (end)')
    ax4.set_yticklabels([])
    ax4.spines['right'].set_visible(False)
    ax4.spines['top'].set_visible(False)

    # set figure size and save
    fig = plt.gcf()
    fig.set_size_inches(5, 3.5)
    plt.tight_layout(pad=0.25, h_pad=-0.5, w_pad=0.5)
    if savefig:
        fig.savefig(OUT_DIR+'fig-scanner-running-analog.png', dpi=450) 


def plot_analog_filtering_scanner_on_close(savefig=False):
    # multiband 1 
    digital_noise_df = load_dataset('../logs/log_5min_scanner_close_sb_new')
    noise_y_unfilt = digital_noise_df.y3
    noise_t = digital_noise_df.t
    noise_y_unfilt = noise_y_unfilt-np.mean(noise_y_unfilt)
    cutoff_freqs = [100,30,10] # in Hz
    noise_y_filt_1 = digital_noise_df.y2-np.mean(digital_noise_df.y2)
    noise_y_filt_2 = digital_noise_df.y1-np.mean(digital_noise_df.y1)
    noise_y_filt_3 = digital_noise_df.y0-np.mean(digital_noise_df.y0)
    print 'unfiltered: '+str(np.std(signal.detrend(noise_y_unfilt)))
    print '100hz: '+str(np.std(signal.detrend(noise_y_filt_1)))
    print '30hz: '+str(np.std(signal.detrend(noise_y_filt_2)))
    print '10hz: '+str(np.std(signal.detrend(noise_y_filt_3)))
    f,wxx_0 = psd_analysis(noise_y_unfilt)
    f,wxx_1 = psd_analysis(noise_y_filt_1)
    f,wxx_2 = psd_analysis(noise_y_filt_2)
    f,wxx_3 = psd_analysis(noise_y_filt_3)
    plt.ion()
    ax1 = plt.subplot(2,2,3)
    plt.semilogy(f,wxx_3, color=COLORS[0])
    plt.semilogy(f,wxx_2, color=COLORS[1])
    plt.semilogy(f,wxx_1, color=COLORS[2])
    plt.semilogy(f,wxx_0, color=COLORS[3])
    plt.xlim(0,100)
    plt.ylim((1e-11,1e-2))
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Power (N$^2$/Hz)')
    ax1.spines['right'].set_visible(False)
    ax1.spines['top'].set_visible(False)
    plt.legend(['10Hz low-pass','30Hz low-pass','100Hz low-pass','Unfiltered'], fontsize=8)

    # multiband 1
    plot_offset = 0.1
    end_time = 0.5
    plot_end_idx = np.where(noise_t==end_time)[0][0]+1
    noise_t_trunc = noise_t[0:plot_end_idx]
    noise_y_unfilt_trunc = noise_y_unfilt[0:plot_end_idx]
    noise_y_filt_1_trunc = noise_y_filt_1[0:plot_end_idx]
    noise_y_filt_2_trunc = noise_y_filt_2[0:plot_end_idx]
    noise_y_filt_3_trunc = noise_y_filt_3[0:plot_end_idx]
    plt.ion()
    ax2 = plt.subplot(2,2,1)
    plt.plot(noise_t_trunc, noise_y_filt_3_trunc+3*plot_offset, color=COLORS[0])
    plt.plot(noise_t_trunc, noise_y_filt_2_trunc+2*plot_offset, color=COLORS[1])
    plt.plot(noise_t_trunc, noise_y_filt_1_trunc+1*plot_offset, color=COLORS[2])
    plt.plot(noise_t_trunc, noise_y_unfilt_trunc, color=COLORS[3])
    plt.xlim((0,end_time))
    plot_y_padding = 0.0025
    plt.ylim((-plot_offset,4*plot_offset))
    # plt.yticks([0,0.1])
    plt.title('(A) Singleband (center)')
    plt.xlabel('Time (sec)')
    plt.ylabel('Force (N)')
    ax2.spines['right'].set_visible(False)
    ax2.spines['top'].set_visible(False)

    # multiband 2
    # digital_noise_df = load_dataset('../logs/log_4_key_scanner_running_mb2_close')
    digital_noise_df = load_dataset('../logs/log_5min_scanner_close_mb_new')
    noise_y_unfilt = digital_noise_df.y3
    noise_t = digital_noise_df.t
    noise_y_unfilt = noise_y_unfilt-np.mean(noise_y_unfilt)
    cutoff_freqs = [100,30,10] # in Hz
    noise_y_filt_1 = digital_noise_df.y2-np.mean(digital_noise_df.y2)
    noise_y_filt_2 = digital_noise_df.y1-np.mean(digital_noise_df.y1)
    noise_y_filt_3 = digital_noise_df.y0-np.mean(digital_noise_df.y0[0:400])
    print 'unfiltered: '+str(np.std(signal.detrend(noise_y_unfilt)))
    print '100hz: '+str(np.std(signal.detrend(noise_y_filt_1)))
    print '30hz: '+str(np.std(signal.detrend(noise_y_filt_2)))
    print '10hz: '+str(np.std(signal.detrend(noise_y_filt_3)))
    f,wxx_0 = psd_analysis(noise_y_unfilt)
    f,wxx_1 = psd_analysis(noise_y_filt_1)
    f,wxx_2 = psd_analysis(noise_y_filt_2)
    f,wxx_3 = psd_analysis(noise_y_filt_3)
    plt.ion()
    ax3 = plt.subplot(2,2,4)
    plt.semilogy(f,wxx_3, color=COLORS[0])
    plt.semilogy(f,wxx_2, color=COLORS[1])
    plt.semilogy(f,wxx_1, color=COLORS[2])
    plt.semilogy(f,wxx_0, color=COLORS[3])
    plt.xlim(0,100)
    plt.ylim((1e-11,1e-2))
    # plt.xlabel('Frequency (Hz)')
    # plt.ylabel('Power (N$^2$/Hz)')
    ax3.set_yticklabels([])
    ax3.spines['right'].set_visible(False)
    ax3.spines['top'].set_visible(False)

    # multiband 2
    plot_offset = 0.1
    end_time = 0.5
    plot_end_idx = np.where(noise_t==end_time)[0][0]+1
    noise_t_trunc = noise_t[0:plot_end_idx]
    noise_y_unfilt_trunc = noise_y_unfilt[0:plot_end_idx]
    noise_y_filt_1_trunc = noise_y_filt_1[0:plot_end_idx]
    noise_y_filt_2_trunc = noise_y_filt_2[0:plot_end_idx]
    noise_y_filt_3_trunc = noise_y_filt_3[0:plot_end_idx]
    plt.ion()
    ax4 = plt.subplot(2,2,2)
    plt.plot(noise_t_trunc, noise_y_filt_3_trunc+3*plot_offset, color=COLORS[0])
    plt.plot(noise_t_trunc, noise_y_filt_2_trunc+2*plot_offset, color=COLORS[1])
    plt.plot(noise_t_trunc, noise_y_filt_1_trunc+1*plot_offset, color=COLORS[2])
    plt.plot(noise_t_trunc, noise_y_unfilt_trunc, color=COLORS[3])
    plt.xlim((0,end_time))
    plot_y_padding = 0.0025
    plt.ylim((-plot_offset,4*plot_offset))
    # plt.yticks([])
    # plt.xlabel('Time (sec)')
    # plt.ylabel('Force (N)')
    plt.title('(B) Multiband (center)')
    ax4.set_yticklabels([])
    ax4.spines['right'].set_visible(False)
    ax4.spines['top'].set_visible(False)

    # set figure size and save
    fig = plt.gcf()
    fig.set_size_inches(5, 3.5)
    plt.tight_layout(pad=0.25, h_pad=-0.5, w_pad=0.5)
    if savefig:
        fig.savefig(OUT_DIR+'fig-scanner-running-analog-close.png', dpi=450) 


###################################
# sample code for adding 'signal' #
###################################

# signal_start_time = 0.3; signal_end_time = 9.9
# signal_df = load_dataset('../logs/log_3p33hz_press',
#     start_time=signal_start_time, end_time=signal_end_time)
# signal_t = signal_df.t
# signal_y = 0.25*signal_df.y0
# noise_trunc_df = load_dataset('../logs/log_4_key_scanner_running_mb1',
#     start_time=signal_start_time, end_time=signal_end_time)
# noise_trunc_y = noise_trunc_df.y0

# load noise data for frequency analysis (1 channel)

# create other 3 channels with digital filtering

# crop noise data for time series plotting

# load noise data for frequency analysis (4 channels)
# crop noise data for time series plotting

################################
# ANALOG FILTERING: SCANNER ON #
################################

# need to collect new data
# same as with scanner off (load different dataset)
