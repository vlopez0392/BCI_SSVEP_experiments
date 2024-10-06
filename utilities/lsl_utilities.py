from pylsl import StreamInfo, StreamOutlet, StreamInlet, cf_double64, cf_string, resolve_stream

###Stream outlet
def eegStreamOut(stream_name, sf, num_ch, id):
    stream_info = StreamInfo(name = stream_name, type = 'EEG', channel_count= num_ch, nominal_srate = sf, 
                  channel_format = cf_double64, source_id = id)

    return StreamOutlet(stream_info);

def markerStreamOut(stream_name, id, sf= 0, num_ch = 1):
    stream_info = StreamInfo(name = stream_name, type = 'Markers', channel_count= 1, nominal_srate = 0, 
                  channel_format = cf_string, source_id = id)

    return StreamOutlet(stream_info);

###Stream inlet 
def eegStreamIn(stream_name, sf, num_ch, id):
    stream_info = StreamInfo(name = stream_name, type = 'EEG', channel_count= num_ch, nominal_srate = sf, 
                  channel_format = cf_double64, source_id = id)

    return StreamInlet(stream_info, max_buflen=sf);

def markerStreamIn(stream_name, id, sf= 0, num_ch = 1):
    stream_info = StreamInfo(name = stream_name, type = 'Markers', channel_count= 1, nominal_srate = 0, 
                  channel_format = cf_string, source_id = id)

    return StreamInlet(stream_info);

def poll_EEG_stream():
    print("Looking for EEG data streams"); 
    streams = resolve_stream('type','EEG');

    ###Get stream info about the EEG device and print it to the console
    streamInfo = streams[0];
    print("Stream name: " , streamInfo.name());
    print("Unique ID: ", streamInfo.uid());
    print("Number of Channels: ", streamInfo.channel_count());
    print("Channel format: ", streamInfo.channel_format());
    print("Sampling Rate: ", streamInfo.nominal_srate());

    return True
    
