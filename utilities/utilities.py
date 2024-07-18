import pandas as pd 
import numpy as np
import csv 
from mne import create_info, Annotations
import matplotlib.pyplot as plt
import matplotlib.colors as pcolors

######## Stimulus paradigm
##Convert ms to frames 
def convertMStoFrames(refresh_rate, time_ms):
    delta = 1000/refresh_rate
    return np.round(time_ms/delta).astype(int)

######## File I/0
##Write CSV file from list of tuples 
def write_tuple_to_CSV(filepath, data_tup_list, header):
    with open(filepath,'w', newline='' ) as file:
        writer = csv.writer(file)
        writer.writerow(header)
        for tup in data_tup_list:
            writer.writerow([tup[0], tup[1]])

###Write a CSV fie from a list of lists
def write_rows_to_CSV(filepath, data_tup_list, header):
    with open(filepath,'w', newline='' ) as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(data_tup_list)


######## Data analysis
###Create mne info object based on the desired deeg device
def createInfoObject(name, types = 'eeg'):
    print("Now creating mne info object for " + str(name) + str(types) + " device ")
    
    ### For now leave these hard-coded info parameters for the Cygnus device. 
    ### In the future, we might want to read from a file to set them given another device 
    n_channels = 32
    sampling_freq = 500.0
    ch_names = [ "Fp1","Fp2","AF3","AF4","F7","F3","Fz","F4","F8","FT7","FC3","FCz","FC4","FT8","T7","C3","Cz","C4","T8","TP7","CP3","CPz","CP4","TP8","P7","P3","Pz","P4","P8","O1","Oz","O2"]
    ch_types = ["eeg"] * n_channels
    info = create_info(ch_names, ch_types=ch_types, sfreq=sampling_freq)
    info.set_montage("standard_1020")
    
    return info     

###Marker streams related functionality
def createMarkerDF(marker_filepath, broadcast_marker, paradigm_onset_delay):
    df = pd.read_csv(marker_filepath) 
    df = df[df['Marker'] != broadcast_marker]
    df = df.reset_index(drop = True)
    df['Time_stamp'] = np.round(df['Time_stamp'] - df['Time_stamp'] [0] + paradigm_onset_delay).astype(float)

    return df

def createAnnotationObject(marker_df, end_stim, end_exp):
    markers = list(marker_df['Marker'])
    ts = list(marker_df['Time_stamp'])
    onset = []
    description = []
    duration = []

    for idx in range(len(markers)):
        if markers[idx]!= end_stim and markers[idx] != end_exp:
            onset.append(ts[idx])
            description.append(markers[idx])

        elif markers[idx] == end_stim:
            duration.append(ts[idx]- ts[idx-1])

    return Annotations(onset = onset, duration = duration, description = description)

######## Plotting utilities
###Save figure to filepath given SSVEP frequency
def getFP(tf, plot_type = 'eeg'):
    if tf == 7.5:
        return './plots/eeg_plots/7_5Hz/' if plot_type == 'eeg' else './plots/psd_plots/7_5Hz/'
        
    elif tf == 10:
        return './plots/eeg_plots/10Hz/' if plot_type == 'eeg' else './plots/psd_plots/10Hz/'

def getFileNames(tf, plot_type = 'eeg'):
    if tf == 7.5:
        return '7_5Hz_EEG.png' if plot_type == 'eeg' else 'avPSD_7_5Hz.png'
        
    elif tf == 10:
        return '10Hz_EEG.png' if plot_type == 'eeg' else 'avPSD_10Hz.png'
    
####EEG
def getEEGParams(tf):
    if tf == 7.5: 
        return {"start": 2, "duration":15, "scalings": dict(eeg = 3000e-1)}
    elif tf == 10: 
        return {"tmin": 20, "tmax":14, "scalings": dict(eeg = 3000e-1)}

def plotEEG(mne_Raw,tf, params, picks, saveFig = False):
    [start, duration, scalings] = list(params.values())    
    fig = mne_Raw.plot(start = start, duration = duration, show_scalebars=True, picks = picks, block = True, scalings = scalings)

    if saveFig:
        fp = getFP(tf)
        fileName = getFileNames(tf)
        fig.savefig(fp+fileName)
    return True

###PSD
###Returns a dictionary of best parameters for plotting PSD and EEG signals based on target SSVEP frequencies 
def getPSDParams(tf):
    if tf == 7.5: 
        return {"tmin": 6.5, "tmax":14, "fmin":3, "fmax":65}
    elif tf == 10: 
        return {"tmin": 24, "tmax":33, "fmin":3, "fmax":65}
    
###PlotAveragePSD
def plotAveragePSD(mneRaw, tf, params, picks, saveFig = False):
    [tmin, tmax,fmin,fmax] = list(params.values())
    fig = mneRaw.compute_psd(method = 'welch', fmin=fmin, fmax = fmax, tmin=tmin ,tmax=tmax, picks = picks).plot(average = True)

    if saveFig:
        fp = getFP(tf, plot_type='psd')
        fileName = getFileNames(tf, plot_type='psd')
        fig.savefig(fp+fileName)

    plt.show()
    return True

###Returns dictionary of CSS colors to plot spectrum densities of O and P eeg channels
def getOP_colors(ch):
    css = pcolors.CSS4_COLORS
    
    colordic = {"P7":"darkgreen", 
                "P3":"rebeccapurple",
                "Pz":"teal",
                "P4":"maroon",
                "P8":"navy",
                "O1":"darkorange",
                "Oz":"crimson",
                "O2":"deeppink"}
    
    return css[colordic[ch]]

###Plot channel PSD
def plotChannelPSD(mneRaw, tf, params, picks, saveFig = False):
        [tmin, tmax,fmin,fmax] = list(params.values())

        for ch in picks:
            spect = mneRaw.compute_psd(method = 'welch', fmin=fmin, fmax = fmax, tmin=tmin ,tmax=tmax, picks = ch)
            _, ax = plt.subplots()
            fig= spect.plot(axes = ax, color = getOP_colors(ch), spatial_colors = False)
            ax.set_title("PSD of " + str(ch) + " channel at " + str(tf) + "Hz target frequency")
            
            if saveFig:
                fp = getFP(tf, plot_type='psd')
                fig.savefig(fp+ch+'png')
            
            plt.show()



