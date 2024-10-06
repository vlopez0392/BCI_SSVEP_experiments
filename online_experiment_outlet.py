import matplotlib.pyplot as plt 
import utilities.lsl_utilities as lsls_utils
from scipy.io import loadmat
from pylsl import resolve_byprop, StreamInlet

###Channel location, frequency, phase and eeg data 
ch_loc_path = './subjects/64-channels.loc'
subject = 'S1';
eeg = loadmat('./subjects/' + subject + '.mat') 
freq_phase = loadmat('./subjects/Freq_Phase.mat') 
print(freq_phase);
sf = 250;
num_ch = 64

###Channels of interest: Pz, PO5, PO3, POz, PO4, PO6, O1, Oz, O2 [48, 54, 55, 56, 57, 58, 61, 62, 63] in channels.loc file 
###Stream data of interest 
target_freq = 12.0;
target_found = False
duration = 6.0;
eeg_data = eeg['data'][:,:,4,5] ##Fourth target, Sixth trial, target frequency is 12.0 Hz

eegStream = lsls_utils.eegStreamOut("benchEEG", sf, eeg_data.shape[0] , "test3000");
mrkStreamIn = lsls_utils.markerStreamIn("mrkIn", "test_marker_3000_in")

print("Streaming data from benchmark eeg outlet")
while not target_found: 

    for sample in range(int(sf*duration)):
        eegStream.push_sample(eeg_data[:,sample])

    ##Keep streaming until task is done in the backend
    streams = resolve_byprop("name", "task_done", timeout=1.0);  ###Resolve by prop otherwise will resolve EEG outlet in this file.
    if len(streams)>0:
        print("Task done!")
        mrk_st = StreamInlet(streams[0]);
        mrk, tst = mrk_st.pull_sample();

        if mrk[0] == "task_done":
            target_found = True

    streams = [];