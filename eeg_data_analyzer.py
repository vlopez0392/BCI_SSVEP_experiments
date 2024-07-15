import pandas as pd 
import os
import matplotlib.pyplot as plt
import numpy as np
from mne import create_info, Annotations
from mne.io import RawArray

###Global variables 
paradigm_onset_delay = 6.0 ##Initial Text and Fixation cross 
eeg_filepath = './trials/csv/trial1eeg.csv'
marker_filerpath = './trials/csv/trial1marker.csv'
broadcast_marker = 'wait'; ##Marker sent when first broadcasting the marker stream

###Create the info object for our EEG raw data
n_channels = 32
sampling_freq = 500.0
ch_names = [ "Fp1","Fp2","AF3","AF4","F7","F3","Fz","F4","F8","FT7","FC3","FCz","FC4","FT8","T7","C3","Cz","C4","T8","TP7","CP3","CPz","CP4","TP8","P7","P3","Pz","P4","P8","O1","Oz","O2"]
ch_types = ["eeg"] * 32
info = create_info(ch_names, ch_types=ch_types, sfreq=sampling_freq)
info.set_montage("standard_1020")
occ_all = ["P3","P7","Pz","P4","P8","O1","Oz","O2"]
Pp = ["P3","P7","Pz","P4","P8"]
Occ = ["O1","Oz","O2"]
print(info)

###Create Raw Array and visualize chosen channels
eeg_df = pd.read_csv(eeg_filepath)
print(eeg_df.head())

eeg_data = np.array(eeg_df.drop("Time_stamp", axis = 1, inplace=False).T)
print(eeg_data)

eeg_raw = RawArray(eeg_data, info)

eeg_raw.set_eeg_reference(["Cz"], projection=False, verbose = False)
eeg_raw.filter(0.1,None, fir_design = "firwin")
eeg_raw.notch_filter(freqs = (60,120))

###Adding events to the raw object - TODO: Create annotations object to plot markers
markers = pd.read_csv(marker_filerpath) 
markers = markers[markers['Marker'] != broadcast_marker]
markers = markers.reset_index(drop = True)
markers['Time_stamp'] = np.round(markers['Time_stamp'] - markers['Time_stamp'] [0] + paradigm_onset_delay).astype(float)
print(markers.head())

###Plot results 
eeg_raw.plot(show_scrollbars=True, show_scalebars=True, picks = Occ, block = True, scalings = 'auto')

eeg_raw.compute_psd(method = 'welch', fmin=3, fmax = 100, tmin=7, tmax=14, picks = occ_all).plot( average = True)
plt.show()
                