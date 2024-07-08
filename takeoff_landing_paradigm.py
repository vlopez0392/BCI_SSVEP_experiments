###Takeoff-landing training paradigm 
import psychopy.visual as visual
import psychopy.core  as core
from pylsl import StreamInfo, StreamOutlet, resolve_stream, StreamInlet, cf_string, local_clock
import numpy as np
import utilities
import socket 

###Globals
win = None
mrkstream_out = None 
results_in = None
fixation = None
is_fullscreen = False
bg_color = [0, 0, 0]
win_w = 800
win_h = 600
refresh_rate = 60 ###Screen refresh rate
num_trials = 1
PARADIGM_NAME = 'takeoff_landing'

###Connect to LabRecorder 
s = socket.create_connection(("localhost", 22345));

####STIMULUS FUNCTIONS
## Display flickering stimulus to screen 
def drawFlickeringStimulus(refresh_rate, frequency, my_win, time_dur):
    if(refresh_rate == 60):
        if(frequency not in [7.5,10,15]):
            print("Cannot display this flickering stimulus at {} Hz refresh rate".format(refresh_rate));
            return False
        else: 
            stim_clock = core.CountdownTimer(time_dur)
            frame_on_off = np.round(0.5*(refresh_rate/frequency)).astype(int);

            onPattern =  visual.GratingStim(win = my_win, name = 'on_pattern', 
                                            units = 'pix', tex = None, pos = [0,0],
                                            color = [1,1,1], colorSpace = 'rgb', opacity = 1,
                                            interpolate = True, size = 100, sf = 1)
            
            
            offPattern =  visual.GratingStim(win = my_win, name = 'off_pattern', 
                                            units = 'pix', tex = None, pos = [0,0],
                                            color = [-1,-1,-1], colorSpace = 'rgb', opacity = 1,
                                            interpolate = True, size = 100, sf = 1)
            ###Begin stimulus
            while stim_clock.getTime() > 0:
                onPattern.setAutoDraw(True)

                for frame in range(frame_on_off):
                    my_win.flip()

                onPattern.setAutoDraw(False)
                offPattern.setAutoDraw(True)

                for frame in range(frame_on_off):
                    my_win.flip()
                    
                offPattern.setAutoDraw(False)

        return True

### Draw a fixation cross to focus on the stimuli 
def drawFixationCross(my_win, time_dur):
    rect_hor = visual.Rect(win = my_win, units='pix', 
                pos=(0, 0), ori = 0,
                width = 20, height = 100, fillColor=[1.0, -1.0, -1.0], lineColor=[1.0, -1.0, -1.0] )
    
    rect_ver = visual.Rect(win = my_win, units='pix', 
            pos=(0, 0), ori = 90,
            width = 20, height = 100, fillColor=[1.0, -1.0, -1.0], lineColor=[1.0, -1.0, -1.0] )
    
    stim_clock = core.CountdownTimer(time_dur)
    while stim_clock.getTime() > 0:
        rect_hor.draw()
        rect_ver.draw()
        my_win.flip()
    return True

### Draw a blank screen to smooth stimuli transitions 
def drawBlankScreen( my_win, time_dur):
    stim_clock = core.CountdownTimer(time_dur)
    while stim_clock.getTime() > 0:
        my_win.flip()
    return True

### Display text to screen
def displayText(my_text, my_win, time_dur):
    text = visual.TextStim(win = my_win, text = my_text, font='Open Sans', units='pix', 
                pos=(0,0), alignText='center',
                height=36, color=[1, 1, 1])
    
    stim_clock = core.CountdownTimer(time_dur)
    while stim_clock.getTime() > 0:
        text.draw()
        my_win.flip()
    return True

#######MARKER STREAM FUNCTIONS
####Create marker stream
def mrk_stream_out(stream_name, id):
    stream_info = StreamInfo(name = stream_name, type = 'Markers', channel_count= 1, nominal_srate = 0, 
                  channel_format = cf_string, source_id = id)

    return StreamOutlet(stream_info);

def detectMrkStream(mrkOutlet,time_dur):
    str_dur = core.CountdownTimer(time_dur)
    while str_dur.getTime() > 0:
        mrkOutlet.push_sample(['wait'])
    return True

###LSL marker stream outlet and broadcast it for 10s to start recording
par_mrk_st = mrk_stream_out(PARADIGM_NAME, 'par1')
print("Broadcasting takeoff and landing marker stream...")

###Once the streams are available, start recording
s.sendall(b"update\n")
s.sendall(b"select all\n")
s.sendall(b"start\n")

###Begin Experiment and create window
win = visual.Window(
    screen = 0,
    size=[win_w, win_h],
    units="pix",
    fullscr= is_fullscreen,
    color=bg_color,
    gammaErrorPolicy = "ignore", 
)

time_series_75Hz = None
time_series_10Hz = None

###Training paradigm 
for i in range(num_trials):     
    
    #######DRONE TAKEOFF
    ###Display text for 3.0 s  
    displayText('Drone takeoff, focus on the red cross', win,  time_dur = 3.0)

    ###Display cross for 3.0 s 
    drawFixationCross(win,  time_dur = 3.0)
    
    ###Display flickering stimulus for 5.0s and send event marker to start recording
    par_mrk_st.push_sample(['takeoff'])
    drawFlickeringStimulus(refresh_rate, 7.5, win, 5.0)
    par_mrk_st.push_sample(['end_s'])
    drawBlankScreen(win, 1.0)

    #######DRONE LANDING 
    ###Display text for 3.0 s  
    displayText('Drone landing, focus on the red cross', win,  time_dur = 3.0)

    ###Display cross for 3.0 s  
    drawFixationCross(win,  time_dur = 3.0)
    
    ###Display flickering stimulus for 2.0s
    par_mrk_st.push_sample(['landing'])
    drawFlickeringStimulus(refresh_rate, 10, win, 5.0)
    par_mrk_st.push_sample(['end_s'])
    drawBlankScreen(win, 1.0)
    
    if i == (num_trials-1):
        par_mrk_st.push_sample(['end'])
        win.close()
        core.wait(1) ###Wait one second before we stop recording
        s.sendall(b"stop\n")
        core.quit()



