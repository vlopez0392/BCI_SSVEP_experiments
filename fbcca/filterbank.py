import numpy as np
import scipy.signal 

##### FBCCA filterbank for realtime eeg 2-D data - Adapted from mnakanishi Github repo 
def filterbank(eeg_data_buffer, sf, fb_idx = 0):

    eeg_data_buffer = np.array(eeg_data_buffer).T
    num_ch, num_samples = eeg_data_buffer.shape

    ##Nyquist Frequency 
    Nq = sf/2 

    ##Passband filter design 
    passband = [6, 14, 22, 30, 38, 46, 54, 62, 70, 78]
    stopband = [4, 10, 16, 24, 32, 40, 48, 56, 64, 72]
    Wp = [passband[fb_idx]/Nq, 90/Nq]
    Ws = [stopband[fb_idx]/Nq, 100/Nq]
    [N, Wn] = scipy.signal.cheb1ord(Wp, Ws, 3, 40) # Band pass filter design
    [B, A] = scipy.signal.cheby1(N, 0.5, Wn, 'bandpass')

    ###We assume we are getting data from a single trial
    y = np.zeros((num_ch, num_samples));

    for ch in range(num_ch):
        ###Apply linear filter twice, once forwards and once backwards 
          y[ch, :] = scipy.signal.filtfilt(B, A, eeg_data_buffer[ch, :], padtype = 'odd', padlen=3*(max(len(B),len(A))-1));

    return y