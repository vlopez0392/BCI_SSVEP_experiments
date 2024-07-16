import pandas as pd 
import numpy as np
import csv 
from mne import create_info, Annotations
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
###Create mne info object based on the desire deeg device
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

def createMarkerDF(marker_filerpath, broadcast_marker, paradigm_onset_delay):
    df = pd.read_csv(marker_filerpath) 
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

###Nice colors for our occipital and parietal eeg channels
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


