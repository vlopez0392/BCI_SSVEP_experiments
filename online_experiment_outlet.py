import matplotlib.pyplot as plt 
import utilities.lsl_utilities as lsl_utils
import utilities.online_utilities as online_utils
import numpy as np
from scipy.io import loadmat
from pylsl import resolve_byprop, StreamInlet
from pylsl.pylsl import LostError
import time

###Send backend results to SSVEP drawing program 
DRAW = True

###Channel location, frequency, phase and eeg data 
###Channels of interest: Pz, PO5, PO3, POz, PO4, PO6, O1, Oz, O2 [48, 54, 55, 56, 57, 58, 61, 62, 63] in channels.loc file 
ch_loc_path = './subjects/64-channels.loc'
subject = 'S1';
eeg = loadmat('./subjects/' + subject + '.mat') 
freq_phase = loadmat('./subjects/Freq_Phase.mat') 
sf = 250;
num_ch = 64

###EEG data related parameters  
target_found = False
duration = 6.0;
GAZE = 250                      
BUFFER = 1000

###Fill a queue with the EEG data
eeg_chunk = np.zeros((BUFFER, num_ch))
eeg_data = eeg['data'] ##Index desired to frequency (8.6 => 24, 10 => 2, 12 => 4 15 => 7)

freq_index_loop = [24,2,4,7]
trial = 1;
eeg_data_queue = online_utils.EEG_data_queue(eeg_data, freq_index_loop, trial);

###Instantiate EEG and task marker streams
eegStreamOut = lsl_utils.eegStreamOut("benchEEG", sf, num_ch , "test3000", chunk_len = BUFFER)
mrk_out = lsl_utils.markerStreamOut("task", "test_mrkr_3000", sf = 0, num_ch = 2)
resolved_backend_stream = False
mrk_back = None
bufferEmpty = True

###Drawing and backend streams
###Wait for drawing program to subscribe to task marker
if DRAW:
    print("Waiting for SSVEP drawing program")
    while not mrk_out.have_consumers():
        mrk_out.push_sample(["task_start", "0"])

###Resolve backend stream 
if not resolved_backend_stream:
    ###Wait for the the backend stream
    print("Waiting for backend stream...")
    streams = resolve_byprop("name", "backend")
    mrk_back = StreamInlet(streams[0], recover = False)

    print("Now streaming data from benchmark eeg outlet")
    print("|-----------------------------------------------------| \n")     
    resolved_backend_stream = True

###Stream EEG data
while not target_found:

    ###Fill in buffer first
    if bufferEmpty: 
        eeg_data = eeg_data_queue.get()
        eeg_data_queue.task_done()
        for sample in range(BUFFER):
            eeg_chunk[sample,:] = eeg_data[:,sample+GAZE].T

        assert eeg_chunk.shape == (BUFFER, num_ch) ###Backend must receive a buffer with the appropriate size
        print("Asserted correct data chunk with size {}".format(eeg_chunk.shape))
        bufferEmpty = False

    ##Pull marker samples from the backend
    try:
        mrk, tst = mrk_back.pull_sample(timeout = 0.5)
    except LostError:
        print("Connection lost or closed!")
        break
    
    if mrk is None:
        print("Buffer full, pushing data")
        eegStreamOut.push_chunk(eeg_chunk);

    if mrk is not None:
        if mrk[0] == "wait":
            print("Waiting for result...")
            
            try:
                mrk, tst = mrk_back.pull_sample() ###Wait for task to be done in backend (timeouts forever)
            except LostError:
                print("Connection lost or closed!")
                break

            if mrk[0] == "back_done":
                print("Got results from backend. Now drawing result \n")
                mrk_out.push_sample([mrk[0], mrk[1]]); ###Send result to drawing program

                if eeg_data_queue.empty():
                    mrk_out.push_sample(["draw_done", "0"])
                    
                    ###Send an array of zeros to signal backend to close EEG stream with grace
                    while eegStreamOut.have_consumers():
                        eegStreamOut.push_chunk(np.zeros((BUFFER, num_ch)));
                    
                    print("EEG data queue is empty and no more subscribers. Closing backend inlet")
                    mrk, tst = mrk_back.pull_sample()
                    if mrk[0] == "all_done":
                        mrk_back.close_stream()

                    target_found = True
                else:
                    bufferEmpty = True
                    time.sleep(5.0);