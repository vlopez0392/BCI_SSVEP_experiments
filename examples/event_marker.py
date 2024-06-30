from pylsl import StreamInfo, StreamOutlet, resolve_stream, StreamInlet
import random
import time

###Outlet stream 
stream_name = 'marker_stream'
stream_type = 'Markers'
n_ch = 1;
sampling_rate = 0; ##Markers are irregular
id = "ID12345"
ch_format = 'string'

info = StreamInfo(name = stream_name, type = stream_type, channel_count= n_ch, nominal_srate = sampling_rate, 
                  channel_format = ch_format, source_id = id)
outlet = StreamOutlet(info);

print("Sending markers...")

while True:
    outlet.push_sample(['Marker'])



