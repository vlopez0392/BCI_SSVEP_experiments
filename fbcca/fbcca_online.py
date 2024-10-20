import numpy as np
from fbcca.filterbank import filterbank as fbank 
from fbcca.cca_reference import cca_reference2 as cca_ref
from scipy.stats import pearsonr 
from sklearn.cross_decomposition import CCA

##### FBCCA - Adapted from mnakanishi Github repo 
'''
Parameters are as follows:
    eeg_data_buffer: Our buffer of real-time EEG data 

    sf: The sampling frequency 

    n_h: Number of harmonics 

    n_fb: Number of sub-band components 
'''

def onlineFBCCA(FREQUENCIES, eeg_data_buffer, sf, n_h = 3, n_fb = 5):
    print("---------------Performing online FBCCA --------------\n")
    fb_coefs = np.power(np.arange(1,n_fb+1),(-1.25)) + 0.25; 
    eeg_data_buffer = np.array(eeg_data_buffer)
    num_samples, num_ch = eeg_data_buffer.shape #num ch x num samples
    num_freq = len(FREQUENCIES)

    y_ref = cca_ref(FREQUENCIES, sf, num_samples)
    cca = CCA(n_components = 1)

    ###Correlation vector 
    r = np.zeros((n_fb, num_freq))

    ###Begin sub-band decomposition 
    curr_r = 0;
    for fb in range(n_fb):
        filt_data = fbank(eeg_data_buffer, sf, fb);

        for f_i in range(num_freq):
            ref_data = np.squeeze(y_ref[f_i,:,:]);
            testC, refC = cca.fit_transform(filt_data.T, ref_data.T)

            curr_r, _ = pearsonr(np.squeeze(testC), np.squeeze(refC));
            r[fb, f_i] = curr_r

    print("Correlation values per sub-band and target frequency: ")
    print(r, "\n")
    rho = np.dot(fb_coefs, r)

    print("Weighed correlation values for all sub-band components and target frequency: ")
    print(rho, "\n")
    print("SSVEP frequency: {} Hz \n".format(FREQUENCIES[np.argmax(rho)]))
    return (True,np.argmax(rho))



