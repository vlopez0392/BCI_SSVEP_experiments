import queue
import numpy as np

####Enqueue EEG data at specific frequencies
def EEG_data_queue(eeg_data, freq_idx, trial_idx):
    if eeg_data.ndim != 4:
        print("Expected a numpy array with 4 dimensions but got {}".format(eeg_data.ndim))
        return None
    
    q = queue.Queue();
    
    for f in range(len(freq_idx)):
        q.put(eeg_data[:,:,freq_idx[f], trial_idx])
    
    return q;