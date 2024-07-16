import pandas as pd 
import os
import matplotlib.pyplot as plt
import numpy as np
from mne.io import RawArray
import utilities.utilities as utils


###Global variables 
paradigm_onset_delay = 6.0 ##Initial Text and Fixation cross 
eeg_filepath = './trials/csv/trial1eeg.csv'
marker_filepath = './trials/csv/trial1marker.csv'
broadcast_marker = 'wait'; ##Marker sent when first broadcasting the marker stream
FREQUENCIES = [7.5, 10]
tmin = 0;
tmax = 100; 
fmin = 3;
fmax= 65;

###Dev variables 
plot = True
save_eeg_plot = False
eeg_7_5Hz_fp = './plots/eeg_plots/7_5Hz/'
eeg_10Hz_fp = './plots/eeg_plots/10Hz/'

save_psd_plot = True
psd_fp = './plots/psd_plots/'

###Create the info object for our EEG raw data
info = utils.createInfoObject(name = 'Cygnus')
occ_all = ["P3","P7","Pz","P4","P8","O1","Oz","O2"]
print(info)

###Create mne Raw Array
eeg_df = pd.read_csv(eeg_filepath)
print(eeg_df.head())
eeg_data = np.array(eeg_df.drop("Time_stamp", axis = 1, inplace=False).T)
eeg_raw = RawArray(eeg_data, info)

###Notch and FIR low-pass filter
eeg_raw.set_eeg_reference('average', projection=False, verbose = False)
eeg_raw.filter(0.1,None, fir_design = "firwin")
eeg_raw.notch_filter(freqs = (60,120))

###Adding events to the raw object
markers = utils.createMarkerDF(marker_filepath, broadcast_marker, paradigm_onset_delay)

###Create annotations object from out marker dataframe
annot = utils.createAnnotationObject(markers, end_stim = 'end_s', end_exp = 'end')
eeg_raw.set_annotations(annot)

###Plot results
target_frequency = 7.5
picks = occ_all


###TODO: All plotting functionality should be imported from utilities.utilities
if plot:
    scalings = dict(eeg = 3000e-1)
    fig = None
    ax = None
    tf_fp = None

    ###Next plot PSD for each channel in target channel and average PSD
    if target_frequency in FREQUENCIES:
        for tf in FREQUENCIES:
            if tf == 7.5:
                tmin = 7
                tmax = 15
                tf_fp = "7_5Hz/"

                ###Plot EEG data for 7.5 Hz
                fig = eeg_raw.plot(start = tmin - 2, duration = 12, show_scalebars=True, picks = occ_all, block = True, scalings = scalings)
                fig.savefig(eeg_7_5Hz_fp +'7_5Hz_eeg.png') if save_eeg_plot else None
            
            elif tf == 10:
                tmin = 24 
                tmax = 33
                tf_fp = "10Hz/"

                ###Plot EEG data for 10 Hz
                fig = eeg_raw.plot(start = tmin - 4, duration = 14, show_scalebars=True, picks = occ_all, block = True, scalings = scalings)
                fig.savefig(eeg_10Hz_fp + '10Hz_eeg.png') if save_eeg_plot else None

        
            ###Plot PSD for each individual target channel
            for ch in picks:
                spect = eeg_raw.compute_psd(method = 'welch', fmin=fmin, fmax = fmax, tmin=tmin ,tmax=tmax, picks = ch)
                _, ax = plt.subplots()
                fig= spect.plot(axes = ax, color = utils.getOP_colors(ch), spatial_colors = False)
                ax.set_title("PSD of " + str(ch) + " channel at " + str(tf) + "Hz target frequency")
                ax.axvline(x = tf, ymin = 0, ymax=1, linestyle = '--', color = utils.getOP_colors(ch))
                fig.savefig(psd_fp+tf_fp+str(ch)+'.png', dpi = 1000) if save_psd_plot else None
                plt.show()

            ###Plot average PSD
            if tf == 7.5:
                fig = eeg_raw.compute_psd(method = 'welch', fmin=fmin, fmax = fmax, tmin=tmin ,tmax=tmax, picks = picks).plot(average = True)
                fig.savefig(psd_fp+tf_fp+'psd_av_7_5Hz.png') if save_psd_plot else None
                plt.show()
            elif tf == 10:
                fig = eeg_raw.compute_psd(method = 'welch', fmin=fmin, fmax = fmax, tmin=tmin ,tmax=tmax, picks = picks).plot(average = True)
                fig.savefig(psd_fp+tf_fp+'psd_av_10Hz.png') if save_psd_plot else None
                plt.show()