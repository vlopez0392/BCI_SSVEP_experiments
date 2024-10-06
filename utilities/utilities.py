import pandas as pd 
import numpy as np
import csv 
from mne import create_info, Annotations
import matplotlib.pyplot as plt
import matplotlib.colors as pcolors
import os

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
def createInfoObject(name, types = 'eeg', ch_names = None, verbose = 40):
    if verbose != 40:
        print("Now creating mne info object for " + str(name) + ' ' + str(types) + " device ")
    
    ### For now leave these hard-coded info parameters for the Cygnus device. 
    ### In the future, we might want to read from a file to set them given another device 

    sampling_freq = 500.0
    
    if ch_names == None:
        ch_names = [ "Fp1","Fp2","AF3","AF4","F7","F3","Fz",
                     "F4","F8","FT7","FC3","FCz","FC4","FT8","T7","C3","Cz","C4","T8","TP7",
                     "CP3","CPz","CP4","TP8","P7","P3","Pz","P4","P8","O1","Oz","O2"]
        
    n_channels = len(ch_names)
    ch_types = ["eeg"] * n_channels
    info = create_info(ch_names, ch_types=ch_types, sfreq=sampling_freq, verbose = verbose)
    info.set_montage("standard_1020")
    
    return info     

###Marker streams related functionality
def createMarkerDF(marker_filepath, broadcast_marker, paradigm_onset_delay):
    df = pd.read_csv(marker_filepath) 
    df = df[df['Marker'] != broadcast_marker]
    df = df.reset_index(drop = True)
    df['Time_stamp'] = np.round(df['Time_stamp'] - df['Time_stamp'] [0] + paradigm_onset_delay).astype(float)

    return df

def createAnnotationObject(marker_df, end_stim, end_exp, dev = False):
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

    if dev:
        print(onset, description, duration)

    return Annotations(onset = onset, duration = duration, description = description)

######## Plotting utilities
###Save figure to filepath given SSVEP frequency
def getFP(tf, paradigm_name, plot_type = 'eeg',):
    root = './plots/' 
    path = None
    
    if plot_type not in ['eeg','psd','fft']:
        print("Invaliid plot type")
        return False
        
    if float.is_integer(float(tf)):
        path = root + plot_type + '_plots/' +  str(tf) + 'Hz/'
    else: 
        path = root + plot_type + '_plots/' + str(tf).replace(".","_") + 'Hz/'

    path += paradigm_name + '/'

    if os.path.exists(path):
        return path
    else: 
        os.mkdir(path)
        return path

###Get filename         
def getFileNames(tf, plot_type = 'eeg', file_format = '.png'):

    if plot_type not in ['eeg','psd','fft']:
        print("Invaliid plot type")
        return False
    
    file_name = str(tf) + 'Hz_' + str.upper(plot_type)

    if not float.is_integer(float(tf)):
        return file_name.replace(".","_") + file_format
    
    return file_name + file_format

####EEG
def getEEGParams(mneRaw, tf, FREQUENCIES, picks, dev = False):
    
    desc = list(mneRaw.annotations.description)
    freq2desc = dict(zip(FREQUENCIES, desc))
    onsets = list(mneRaw.annotations.onset)
    duration = list(mneRaw.annotations.duration)

    start = onsets[desc.index(freq2desc[tf])]
    duration = duration[desc.index(freq2desc[tf])]
    scalings = dict(eeg = 3000e-1)

    return [start, duration, scalings]

def plotEEG(mne_Raw,tf, params, picks, paradigm_name, saveFig = False):
    [start, duration, scalings] = params

    block = False if saveFig else True 

    fig = mne_Raw.plot(start = start, duration = duration, show_scalebars=True, picks = picks, block = block, scalings = scalings)

    if saveFig:
        fp = getFP(tf,paradigm_name)
        print(fp)
        fileName = getFileNames(tf)
        fig.savefig(fp+fileName)
    return True

###PSD
###Returns a dictionary of best parameters for plotting PSD and EEG signals based on target SSVEP frequencies 
def getPSDParams(tf, best_psd_times):

    if best_psd_times[tf] == "reject":
        return False
    
    fmin = 3
    fmax = 80
    tmin = best_psd_times[tf][0]
    tmax = best_psd_times[tf][1]

    return [tmin,tmax,fmin,fmax]

### This function computes the PSD of an eeg signal with variable time windows (min of 2.0 s) with steps of 0.5 s  
### It returns the starting and ending times of an eeg signal whose max PSD value occurs (within a tolerance value) of our target frequency  
def getBestPSDParams(mneRaw, FREQUENCIES, picks, dev = False):
    fmin = 6
    fmax = 24 
    window = 2
    step = 0.5
    sfreq = mneRaw.info["sfreq"]
    
    desc = list(mneRaw.annotations.description)
    freq2desc = dict(zip(FREQUENCIES, desc))
    onsets = list(mneRaw.annotations.onset)
    duration = list(mneRaw.annotations.duration)

    res = {}

    for tf in FREQUENCIES:
        tmin = onsets[desc.index(freq2desc[tf])]
        tmax = tmin + duration[desc.index(freq2desc[tf])]
        tmin += 0.5
        tol = [tf-0.5, tf+0.5]
        within_tol = []
         
        for curr_startp in np.linspace(tmin, tmax-window, 6):
            curr_endp = curr_startp + window
            curr_best = 0

            while curr_endp <= tmax:
                spec =  mneRaw.compute_psd(method = 'welch', n_fft = int(sfreq*(curr_endp-curr_startp)), proj = False, fmin=fmin, fmax = fmax, tmin=curr_startp ,tmax=curr_endp, picks = picks, verbose = 50)
                spec_data, freqs = spec.get_data(picks = picks, fmin = fmin, fmax = fmax, return_freqs = True)
                spec_data = np.average(spec_data, axis = 0)
                
                curr_best = np.abs(freqs[np.argmax(spec_data)])

                if curr_best >= tol[0] and curr_best <= tol[1]:
                    within_tol.append((curr_startp, curr_endp, curr_best))

                    if dev:
                        print(tf, curr_startp, curr_endp, curr_best)

                curr_endp += step

        if len(within_tol) == 0:
            res[tf] = "reject"
        else:
            idx = 0
            min = (1000,0)

            for tup in within_tol:
                curr_min = np.abs(tf - tup[2])
                
                if curr_min < min[0]:
                    min = (curr_min, idx)
                idx +=1
            
            if dev:
                print(min)
        
            res[tf] = within_tol[min[1]]
        
    print("The following time windows return an EEG signal whose max PSD match our target frequencies: \n" )
    print(res)
    return res


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

###Plot PSD
def plotAveragePSD(mneRaw, tf, params, picks, paradigm_name, average = True, saveFig = False):
    [tmin,tmax,fmin,fmax]  = params
    sfreq = mneRaw.info["sfreq"]
    spec = mneRaw.compute_psd(method = 'welch',n_fft = int(sfreq*(tmax-tmin)), proj = True, fmin=fmin, fmax = fmax, tmin=tmin ,tmax=tmax, picks = picks)

    fig = None
    if average == True:
        fig = spec.plot( amplitude = False)

        if saveFig:
            fp = getFP(tf,paradigm_name, plot_type='psd')
            fileName = getFileNames(tf, plot_type='psd')
            fig.savefig(fp+fileName, dpi = 1000)
            plt.close() 
        else:
            plt.show()

    else:
        for ch in picks:
            spect = mneRaw.compute_psd(method = 'welch',n_fft = int(sfreq*(tmax-tmin)), fmin=fmin, fmax = fmax, tmin=tmin ,tmax=tmax, picks = ch)
            _, ax = plt.subplots()
            fig= spect.plot(axes = ax, color = getOP_colors(ch), spatial_colors = False)
            ax.set_title("PSD of channel " + str(ch) + " at " + str(tf) + "Hz target frequency")

            if saveFig:
                fp = getFP(tf,paradigm_name, plot_type='psd')
                fig.savefig(fp+ch+'.png')
                plt.close() 
            else:
                plt.show()
    return True

###FFT
def getFFTParams(tf):
    if tf == 7.5: 
        return {"tmin": 6.5, "tmax":10}
    elif tf == 10: 
        return {"tmin": 25.0, "tmax":31.5}

###Plot FFT 
def plotFFT(mneRaw, info, params, picks, saveFig = True):
    [tmin, tmax] = list(params.values())

    fft_data = mneRaw.get_data(picks = picks, tmin = tmin, tmax = tmax)
    win_size = fft_data.shape[-1];
    freq = np.fft.rfftfreq(win_size, 1/info["sfreq"])
    fftval = np.abs(np.fft.rfft(fft_data, axis = 1))
    fftval = np.average(fftval, axis = 0)
                    
    fig, ax = plt.subplots(1,1)
    ax.plot(freq, fftval.T)
    ax.set_title("abs(FFT)")
    
    plt.show()

    return True