from pylsl import StreamInfo, resolve_stream

def poll_EEG_stream():
    print("Looking for EEG streams"); 
    streams = resolve_stream('type','EEG');

    ###Get stream info about the EEG device and print it to the console
    streamInfo = streams[0];
    print("Stream name: " , streamInfo.name());
    print("Unique ID: ", streamInfo.uid());
    print("Number of Channels: ", streamInfo.channel_count());
    print("Channel format: ", streamInfo.channel_format());
    print("Sampling Rate: ", streamInfo.nominal_srate());

    return True
    
