import pandas as pd 
import os
import numpy as np
from mne.io import RawArray
import utilities.utilities as utils

###Global variables 
paradigm_onset_delay = 6.0 ##Initial Text and Fixation cross 
eeg_filepath = './trials/csv/trial1eeg.csv'
marker_filepath = './trials/csv/trial1marker.csv'
broadcast_marker = 'wait'; ##Marker sent when first broadcasting the marker stream
FREQUENCIES = [7.5, 10]

###Dev variables 
plot = True
plotEEG = True
plotPSD = False
save_eeg_plot = False
save_psd_plot = False

###Create the info object for our EEG raw data
info = utils.createInfoObject(name = 'Cygnus')
occ_all = ["P3","P7","Pz","P4","P8","O1","Oz","O2"]
print(info)

###Create mne Raw Array object
eeg_df = pd.read_csv(eeg_filepath)
print(eeg_df.head())
eeg_data = np.array(eeg_df.drop("Time_stamp", axis = 1, inplace=False).T)
eeg_raw = RawArray(eeg_data, info)

###Notch and FIR low-pass filter
eeg_raw.set_eeg_reference('average', projection=False, verbose = False)
eeg_raw.filter(5,50, fir_design = "firwin")
eeg_raw.notch_filter(freqs = (60,120))

###Adding events to the raw object
markers = utils.createMarkerDF(marker_filepath, broadcast_marker, paradigm_onset_delay)

###Create annotations object from out marker dataframe
annot = utils.createAnnotationObject(markers, end_stim = 'end_s', end_exp = 'end')
eeg_raw.set_annotations(annot)

###Plot results
tf = 10
picks = occ_all
if plot:
    if tf in FREQUENCIES:
        ###Plot EEG 
        if plotEEG:
            eeg_params = utils.getEEGParams(tf)
            utils.plotEEG(eeg_raw, tf, eeg_params, picks = occ_all, saveFig = save_eeg_plot)
        
        ###Plot PSD
        if plotPSD:
            psd_params = utils.getPSDParams(tf)
            utils.plotAveragePSD(eeg_raw, tf, psd_params, picks, saveFig = save_psd_plot)

            ###Plot PSD for each individual target channel
            utils.plotChannelPSD(eeg_raw, tf, psd_params, picks, saveFig = save_psd_plot)




