import pyxdf
import numpy as np
import utilities 

###Load data 
data, header = pyxdf.load_xdf('./trials/marker_test_2.xdf')
markers = []
timestamps = []
results = []
has_written = False
filepath = './plots/marker_plot/mrkr2.csv'

###Save data to csv file
if not has_written:
    for stream in data:
        for k,v in stream.items():
            if k == 'info' or k == 'footer':
                continue
            elif k == 'time_series':
                for marker in v:
                    markers.append(marker[0])
            else: ##timestamps
                for tst in v:
                    timestamps.append(tst)

    results = zip(markers, timestamps);
    utilities.write_tuple_to_CSV(filepath, results, ['Marker','Time_stamp'])