from pylsl import StreamInfo, StreamInlet, resolve_stream
import datetime

print("Looking for EEG streams "); 
streams = resolve_stream('type','EEG');

###Get info about the Stream - EEG device 
streamInfo = streams[0];
print("Got Stream Info object of type: ", type(streamInfo));
print("Stream name: " , streamInfo.name());
print("Unique ID: ", streamInfo.uid());
print("Number of Channels: ", streamInfo.channel_count());
print("Channel format: ", streamInfo.channel_format());
print("Sampling Rate: ", streamInfo.nominal_srate());

###Create a new data inlet and read from the stream 
inlet = StreamInlet(streamInfo)

for i in range(100):
    sample, timestamp = inlet.pull_sample()
    print(timestamp, '\n' ,sample)
    
