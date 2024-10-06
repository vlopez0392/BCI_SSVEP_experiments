import pandas as pd 
import numpy as np
from mne.io import RawArray
import utilities.utilities as utils
import stim.SSVEP as ssvep

###Global variables 
paradigm_onset_delay = 2.0 ##Initial Text and Fixation cross 
broadcast_marker = 'wait'; ##Marker sent when first broadcasting the marker stream
verbose = 40
FREQUENCIES = ssvep.getValidFrequencies(refresh_rate=60)

###Dev variables 
plot = False
plotEEG = True
plotPSD = False
save_eeg_plot = False
save_psd_plot = False
plotFFT = False

for trial in range(1,7):
    eeg_filepath = './trials/csv/all_eeg_targets_trial' + str(trial) + '.csv'
    marker_filepath = './trials/csv/all_mrk_targets_trial' + str(trial) + '.csv'
    PARADIGM_NAME = 'all_targets_trial' + str(trial)

    ###Create the info object for our EEG raw data
    occ_all = ["P3","P7","Pz","P4","P8","O1","Oz","O2"]
    occ = ["O1","Oz","O2"]
    par = ["P3","P7","Pz","P4","P8"]
    info = utils.createInfoObject(name = 'Cygnus')
    all = info["ch_names"]

    ###Create mne Raw Array object
    eeg_df = pd.read_csv(eeg_filepath)
    eeg_df = eeg_df.drop("Time_stamp", axis = 1, inplace=False).T
    eeg_data = np.array(eeg_df)
    eeg_raw = RawArray(eeg_data, info, verbose = verbose)

    ###Notch and FIR low-pass filter
    eeg_raw.set_eeg_reference("average", projection=False, verbose = verbose)
    eeg_raw = eeg_raw.filter(6,50, fir_design = "firwin", verbose = verbose)
    eeg_raw = eeg_raw.notch_filter(freqs = (60), verbose = verbose)

    ###Adding events to the raw object
    markers = utils.createMarkerDF(marker_filepath, broadcast_marker, paradigm_onset_delay)

    ###Create annotations object from out marker dataframe
    print("Current trial: " + str(trial))
    annot = utils.createAnnotationObject(markers, end_stim = 'end_s', end_exp = 'end', dev = False)
    eeg_raw.set_annotations(annot)

    ###Plot results
    picks = occ_all
    best_psd = utils.getBestPSDParams(eeg_raw, FREQUENCIES, picks, dev = True)
    for tf in FREQUENCIES:
        if plot:
            ###Plot EEG 
            if plotEEG:
                eeg_params = utils.getEEGParams(eeg_raw, tf, FREQUENCIES, picks)
                utils.plotEEG(eeg_raw, tf, eeg_params, picks = picks, paradigm_name = PARADIGM_NAME, saveFig = save_eeg_plot)
            
            ###Plot PSD
            if plotPSD:
                psd_params = utils.getPSDParams(tf, best_psd)

                if psd_params != False:
                    utils.plotAveragePSD(eeg_raw, tf, psd_params, picks = picks, paradigm_name = PARADIGM_NAME, average = False, saveFig = save_psd_plot)

            ###Plot FFT
            if plotFFT:
                fft_params = utils.getFFTParams(tf)
                utils.plotFFT(eeg_raw, info, fft_params, picks = occ, saveFig = True)



