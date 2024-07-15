import pyxdf
import numpy as np
import utilities.utilities as utilities 

###Load data 
data, header = pyxdf.load_xdf('./trials/xdf/trial2.xdf')
eeg = []
channel_labels = []
markers = []
mrk_timestamps = []
results = []
has_written = False
eeg_filepath = './trials/csv/trial2eeg.csv'
marker_filepath = './trials/csv/trial2marker.csv'
curr_stream_name = None
eeg_stream_name = 'Cygnus-329004-RawEEG'
paradigm_stream_name = 'takeoff_landing'

###Save eeg and marker data to separate csv files
if not has_written:
    for stream in data:
        for k,v in stream.items():
            if k == 'info':
                curr_stream_name = v['name'][0]
                print("Now writing " + str(curr_stream_name) + ".csv file")

                if curr_stream_name == eeg_stream_name:
                    channels = v['desc'][0]['channels'][0]['channel']
                    for ch in channels:
                        channel_labels.append(ch['label'][0])
            
            elif k == 'time_series':
                if curr_stream_name == eeg_stream_name:
                    for ts in v:
                        eeg.append(list(ts))
                elif curr_stream_name == paradigm_stream_name:
                    for marker in v:
                        markers.append(marker[0])

            elif k == 'time_stamps':
                if curr_stream_name == eeg_stream_name: 
                    idx = 0
                    for tst in v:
                        eeg[idx].append(tst)
                        idx+=1
            
                    channel_labels.append('Time_stamp')
                    utilities.write_rows_to_CSV(eeg_filepath, eeg, channel_labels)
                
                elif curr_stream_name == paradigm_stream_name:
                    for tst in v:
                        mrk_timestamps.append(tst)

                    results = zip(markers, mrk_timestamps);
                    utilities.write_tuple_to_CSV(marker_filepath, results, ['Marker','Time_stamp'])