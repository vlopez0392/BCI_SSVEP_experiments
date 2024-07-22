###Takeoff-landing training paradigm 
import psychopy.core  as core
from pylsl import StreamInfo, StreamOutlet, resolve_stream, StreamInlet, cf_string, local_clock
import socket 
import poll_EEG_stream as eeg_stream
import stim.SSVEP as ssvep

###Global variables
###Window
win = None
mrkstream_out = None 
results_in = None
fixation = None
is_fullscreen = True
bg_color = [0, 0, 0]
win_w = 800
win_h = 600
refresh_rate = 60 ###Screen refresh rate
my_screen = 1;
winType = 'pyglet'

###Paradigm variables
NUM_TRIALS = 1
PARADIGM_NAME = 'takeoff_landing'
FREQUENCIES =  ssvep.getValidFrequencies(refresh_rate)

##Development variables 
record_Data = False
broadcast_dur = 1.0
poll_eeg = False

#######MARKER STREAM FUNCTIONS
####Create marker stream
def mrk_stream_out(stream_name, id):
    stream_info = StreamInfo(name = stream_name, type = 'Markers', channel_count= 1, nominal_srate = 0, 
                  channel_format = cf_string, source_id = id)

    return StreamOutlet(stream_info);

def detectMrkStream(mrkOutlet,time_dur, lr_socket):
    print("Broadcasting takeoff and landing marker stream...")
    str_dur = core.CountdownTimer(time_dur)
    start_lr = False;

    while str_dur.getTime() > 0:
        mrkOutlet.push_sample(['wait'])

        if not start_lr:
            ###Once the streams are available, start recording with labrecorder
            lr_socket.sendall(b"update\n")
            lr_socket.sendall(b"select all\n")
            lr_socket.sendall(b"start\n")    
            start_lr = True;
    return True

###Begin experiment
###LSL marker stream outlet
par_mrk_st = mrk_stream_out(PARADIGM_NAME, 'par1')

if record_Data:
    if poll_eeg:
        ###Resolve eeg stream 
        eeg_stream.poll_EEG_stream();
    
    #####Connect to LabRecorder 
    lr_socket = socket.create_connection(("localhost", 22345))
    ##Resolve marker stream    
    detectMrkStream(par_mrk_st, broadcast_dur, lr_socket)
    
###Create window
win = ssvep.createWindow(my_screen,win_w,win_h,is_fullscreen,bg_color,winType);

##Training paradigm
for i in range(NUM_TRIALS):     
    
    #######DRONE TAKEOFF
    ###Display text for 3.0 s  
    ssvep.displayText('Drone takeoff, focus on the red cross', win,  time_dur = 3.0)

    ###Display cross for 3.0 s 
    ssvep.drawFixationCross(win,  time_dur = 3.0)
    
    ###Display flickering stimulus for 5.0s and send event marker to start recording
    par_mrk_st.push_sample(['takeoff'])
    ssvep.drawFlickeringStim(FREQUENCIES, refresh_rate, 7.5, win, 5.0)
    par_mrk_st.push_sample(['end_s'])
    ssvep.drawBlankScreen(win, 1.0)

    ###DRONE LANDING 
    ###Display text for 3.0 s  
    ssvep.displayText('Drone landing, focus on the red cross', win,  time_dur = 5.0)

    ###Display cross for 3.0 s  
    ssvep.drawFixationCross(win,  time_dur = 3.0)
    
    ###Display flickering stimulus for 2.0s
    par_mrk_st.push_sample(['landing'])
    ssvep.drawFlickeringStim(FREQUENCIES, refresh_rate, 10, win, 3.0)
    par_mrk_st.push_sample(['end_s'])
    ssvep.drawBlankScreen(win, 1.0)
    
    if i == (NUM_TRIALS-1):
        par_mrk_st.push_sample(['end'])
        win.close()
        core.wait(1) ###Wait one second before we stop recording
        if record_Data:
            lr_socket.sendall(b"stop\n")
        core.quit()




