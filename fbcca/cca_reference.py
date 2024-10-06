import numpy as np;

#####Create sinusoidal reference signals for CCA - No need for tmp variable
def cca_ref(FREQUENCIES, sf, buffer_size, n_h = 3):
    
    t = np.arange(1, buffer_size+1)/sf;
    n_f = len(FREQUENCIES)
    y_ref = np.zeros((n_f, 2*n_h, buffer_size)); 
    freq = None;

    for f_i in range(n_f):
        freq = FREQUENCIES[f_i]
        k = 1

        for h_i in np.arange(0,2*(n_h),2):
            y_ref[f_i][h_i]   = np.sin(2*np.pi*(h_i+ k)*freq*t);
            y_ref[f_i][h_i+1] = np.cos(2*np.pi*(h_i+ k)*freq*t);
            k+=-1;

    return y_ref

###Nakanishi's version adapted from MATLAB
def cca_reference2(list_freqs, fs, num_smpls, num_harms=3):
    
    num_freqs = len(list_freqs)
    tidx = np.arange(1,num_smpls+1)/fs #time index
    
    y_ref = np.zeros((num_freqs, 2*num_harms, num_smpls))
    for freq_i in range(num_freqs):
        tmp = []
        for harm_i in range(1,num_harms+1):
            stim_freq = list_freqs[freq_i]  #in HZ
            # Sin and Cos
            tmp.extend([np.sin(2*np.pi*tidx*harm_i*stim_freq),
                       np.cos(2*np.pi*tidx*harm_i*stim_freq)])
        y_ref[freq_i] = tmp # 2*num_harms because include both sin and cos
    
    return y_ref
        