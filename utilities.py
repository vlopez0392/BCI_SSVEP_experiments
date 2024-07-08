import numpy as np
import csv 

##Convert ms to frames 
def convertMStoFrames(refresh_rate, time_ms):
    delta = 1000/refresh_rate
    return np.round(time_ms/delta).astype(int)

##Write CSV file from list of tuples 
def write_tuple_to_CSV(filepath, data_tup_list, header):
    with open(filepath,'w', newline='' ) as file:
        writer = csv.writer(file)
        writer.writerow([header[0], header[1]])
        for tup in data_tup_list:
            writer.writerow([tup[0], tup[1]])

