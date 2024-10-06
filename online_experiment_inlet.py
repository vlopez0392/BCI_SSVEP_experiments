import matplotlib.pyplot as plt 
import utilities.lsl_utilities as lsls_utils
import numpy as np
import fbcca.fbcca_online as fbcca
from scipy.io import loadmat
from pylsl import resolve_stream, StreamInlet


###Sampling frequency and number of eeg channels 
sf = 250
num_ch = 64
BUFFER = 1000
target_frequency = 8.0 

####Target frequencies 
FREQUENCIES = [8.2, 10.0, 12.0, 15.0]

####Fill in a buffer with data from a stream outlet 
bufferFull = False; 
resolved_stream = False

while not bufferFull: 
    if not resolved_stream:
        print("Looking for eeg streams")
        streams = resolve_stream('type', 'EEG')
        eeg_stream_in = StreamInlet(streams[0], max_buflen=BUFFER)
        resolved_stream = True
    
    ###Perform analysis here
    data, time = eeg_stream_in.pull_chunk(timeout=1.1, max_samples=BUFFER);

    ###Perform fbcc
    fbcca.onlineFBCCA(FREQUENCIES, data, sf);

    ####Once task is done, stop EEG outlet. 
    if len(data) == BUFFER:
        mrk_out = lsls_utils.markerStreamOut("task_done", "test_mrkr_3000")
        for _ in range(BUFFER):
            mrk_out.push_sample(["task_done"])
        bufferFull = True;
