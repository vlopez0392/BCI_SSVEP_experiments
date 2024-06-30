import pandas as pd
import numpy as np
import matplotlib.pyplot as plt 

####Load CSV files 
markers = pd.read_csv('./mrkr.csv') 
paradigm_onset_delay = 6; ##Initial Text and Fixation cross 

markers['Time_stamp'] = np.round(markers['Time_stamp'] - markers['Time_stamp'] [0] + paradigm_onset_delay).astype(int)
print(markers[:-1])

####Plot markers 
def plotOnsetMarkers(df, num_trials):
    tst = df['Time_stamp'][:-1]
    mrk = df['Marker'][:-1]
    color_dic = {'takeoff':'b', 'landing':'r', 'end_s':'g', 'end':'k'}

    for t,m in zip(tst,mrk):
        plt.scatter(t, 1, color = color_dic[m])
        plt.axvline(t, ymin = 0.25, ymax=0.75, linestyle = '--', color = color_dic[m] )
        if m =='end_s':
            plt.annotate(m, (float(t-1), float(1.03)))
        elif m == 'end':
            plt.annotate(m, (float(t-0.5), float(0.96)))
        else:
            plt.annotate(m, (float(t-2), float(0.96))) 

    plt.title('Stimulus Event Markers for ' + str(num_trials) + ' trials') 
    plt.xlabel('Time (s)')
    plt.ylabel('Marker Onset')
    plt.xticks(np.arange(0, 52, 3.0))
    plt.xlim((0, 52))
    plt.grid(True, which = 'both')
    plt.show()

plotOnsetMarkers(markers, 3)
