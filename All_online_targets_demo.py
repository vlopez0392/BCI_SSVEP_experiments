###Present multiple targets to the user simultaneously
import psychopy.core as core
import socket 
import poll_EEG_stream as eeg_stream
import stim.SSVEP as ssvep
import threading, time
import utilities.lsl_utilities as lsl_utils
from pylsl import resolve_stream, resolve_byprop, StreamInlet
from scipy.io import loadmat

###Global variables
###Window
win = None
mrkstream_out = None 
results_in = None
fixation = None
is_fullscreen = False
bg_color = [0, 0, 0]
win_w = 1200
win_h = 1000
refresh_rate = 60 ###Screen refresh rate
my_screen = 1;
winType = 'pyglet'

###Paradigm variables
NUM_TRIALS = 1
PARADIGM_NAME = 'all_online_targets'
FREQUENCIES = ssvep.getValidFrequencies(refresh_rate)
TARGET_FREQUENCIES =  FREQUENCIES[2:]
TASK = True

###Wait for task marker stream if performing online experiment
if TASK:
    task_mrk_st = None
    print("Looking for task stream")
    streams = resolve_byprop("name", "task");
    task_mrk_st = StreamInlet(streams[0]);

    if task_mrk_st is not None:
        print("Found task stream!")

# ###Create window
win = ssvep.createWindow(my_screen,win_w,win_h,is_fullscreen,bg_color,winType);

# ###Draw multiple flickers in screen
while True:
    ssvep.drawMultipleFlicker(FREQUENCIES, win, refresh_rate, TARGET_FREQUENCIES, 600, task_mrk_st);

