import time
import utilities.lsl_utilities as lsls_utils
import fbcca.fbcca_online as fbcca
import numpy as np
from scipy.io import loadmat
from pylsl import resolve_byprop, StreamInlet
from pylsl.pylsl import LostError

###Sampling frequency and number of eeg channels 
sf = 250
num_ch = 64
BUFFER = 1000
target_frequency = 8.0 

####Target frequencies 
FREQUENCIES = [8.6, 10.0, 12.0, 15.0]

####EEG and task stream inlet variables
resolved_streams = False
data = np.zeros((BUFFER, num_ch));
taskDone = False
mrk = None

###Instantiate backend marker stream
back_mrk_out = lsls_utils.markerStreamOut("backend", "test_mrkr_3000", sf = 0, num_ch = 2)

print("Starting backend marker stream")
while not back_mrk_out.have_consumers():
    back_mrk_out.push_sample(["start", "0"])

###Resolve test EEG stream    
if not resolved_streams:
    print("Looking for EEG and task streams \n")

    streams = resolve_byprop("name", "benchEEG")
    print("Got EEG stream with name {}".format(streams[0].name()))
    print("|-----------------------------------------------------| \n")

    eeg_stream_in = StreamInlet(streams[0], max_chunklen=BUFFER, recover = False) 
    
    resolved_streams = True

### Pull chunk of data and fill the buffer
while not taskDone: 
    try:
        _, tst = eeg_stream_in.pull_chunk(timeout=7.0, max_samples= BUFFER, dest_obj=data);

        if np.any(data):
            back_mrk_out.push_sample(["wait", "0"]) ##Data received successfully

            ###Perform fbcca
            result, index = fbcca.onlineFBCCA(FREQUENCIES, data, sf);

            ####Once result is returned, send result to task stream
            if result:
                back_mrk_out.push_sample(["back_done", str(index)])
                data = np.zeros((BUFFER, num_ch));
                
        elif not np.any(data):
            eeg_stream_in.close_stream()

            while back_mrk_out.have_consumers():
                back_mrk_out.push_sample(["all_done","0"])

            taskDone = True

    except LostError:
        print("Connection lost or closed!")
        break


