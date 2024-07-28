import psychopy.visual as visual
import psychopy.core  as core
import numpy as np
import keyboard as kb

def createWindow(my_screen, win_w, win_h, is_fullscreen, bg_color, winType):
    return visual.Window(
        screen = my_screen,
        size=[win_w, win_h],
        units="pix",
        fullscr= is_fullscreen,
        color=bg_color,
        winType = winType,
        gammaErrorPolicy = "ignore"
    )

def launchTestWindow():
    return visual.Window(
        screen = 0,
        size=[800, 600],
        units="pix",
        fullscr= True,
        color=[0,0,0],
        winType = 'pyglet',
        gammaErrorPolicy = "ignore"
    )

def getValidFrequencies(refresh_rate):
    if refresh_rate == 60:
        return [6.66, 7.5, 8.57, 10, 12, 15]

######################## SINGLE-PATTERN RELATED FUNCTIONS FOR OFFLINE SSVEP EXPERIMENTS ######################## 

###Get on and off patterns for a single element
def getOnOffPatterns(my_win):
        onPattern =  visual.GratingStim(win = my_win, name = 'on_pattern', 
                                            units = 'pix', tex = None, pos = [0,0],
                                            color = [1,1,1], colorSpace = 'rgb', opacity = 1,
                                            interpolate = True, size = 330, sf = 1)
        
        offPattern =  visual.GratingStim(win = my_win, name = 'off_pattern', 
                                            units = 'pix', tex = None, pos = [0,0],
                                            color = [-1,-1,-1], colorSpace = 'rgb', opacity = 1,
                                            interpolate = True, size = 330, sf = 1)
        
        return (onPattern, offPattern)

###Returns tuple of (on,off) frame durations    
def getOnOffPatternDurations(refresh_rate, tf):
    if tf in getValidFrequencies(refresh_rate):
        evenlyDivisible = 10*int((refresh_rate/tf)%2)

        if evenlyDivisible == 0:
            on_off = np.round(0.5*(refresh_rate/tf)).astype(int);
            return (on_off, on_off)

        else: 
            durations = {6.66:(4,5), 8.57:(3,4), 12:(2,3)}
            return durations[tf]
    else:
        print("Invalid input target frequency {}".format(tf))
        return False
        

## Display flickering stimulus to screen 
def drawFlickeringStim(FREQUENCIES, refresh_rate, frequency, my_win, time_dur):

    if(frequency not in getValidFrequencies(refresh_rate)):
        print("Cannot display this flickering stimulus at {} Hz refresh rate".format(refresh_rate));
        return False
    else: 
        stim_clock = core.CountdownTimer(time_dur)
        (frame_on, frame_off) = getOnOffPatternDurations(refresh_rate,frequency)
        (onPattern, offPattern) = getOnOffPatterns(my_win) 

        ###Begin stimulus
        while stim_clock.getTime() > 0:
            onPattern.setAutoDraw(True)

            for _ in range(frame_on):
                my_win.flip()

            onPattern.setAutoDraw(False)
            offPattern.setAutoDraw(True)

            for _ in range(frame_off):
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

####Get Frame Paths 
def getFramePaths(target_frequencies):
    frameRoot = './pictures/movie_frames/'
    framePaths = {};

    for tf in target_frequencies:

        if float.is_integer(float(tf)):
            framePaths[tf] = frameRoot + str(tf) + 'Hz/frame'
        else:
            framePaths[tf] = frameRoot + str(tf).replace(".","_") + 'Hz/frame'

    return framePaths

### Save frame screenshots and timestamps to verify correct stimiulus presentation 
def saveFlickerFrames(FREQUENCIES, refresh_rate, tf, my_win, time_dur = 1.0):
    
    ###Get paths to write frame screenshots
    framePaths = getFramePaths(FREQUENCIES)
    save_Frames = True

    if(tf not in getValidFrequencies(refresh_rate)):
        print("Cannot display this flickering stimulus at {} Hz refresh rate".format(refresh_rate));
        return False
    else: 
        stim_clock = core.CountdownTimer(time_dur)
        (frame_on, frame_off) = getOnOffPatternDurations(refresh_rate,tf)
        (onPattern, offPattern) = getOnOffPatterns(my_win) 

        ###Begin stimulus
        while stim_clock.getTime() > 0:
            onPattern.setAutoDraw(True)

            for frame in range(frame_on):
                my_win.flip()
                if save_Frames == True:
                    my_win.getMovieFrame()
                    my_win.saveMovieFrames(framePaths[tf] + str(frame) + '.png')

            onPattern.setAutoDraw(False)
            offPattern.setAutoDraw(True)

            for frame in range(frame_off):
                my_win.flip()
                if save_Frames == True:
                    my_win.getMovieFrame()
                    my_win.saveMovieFrames(framePaths[tf] + str(frame+frame_off) + '.png')
                    if frame == frame_off-1:
                        save_Frames = False

            offPattern.setAutoDraw(False)
            
    return True
    
####Write frame screenshots for all target frequencies for single pattern stimuli  
def saveAllFrames(FREQUENCIES):
    win = launchTestWindow()
    refresh_rate = 60;

    for tf in FREQUENCIES:

        ###Display text to indicate current target frequency     
        currTF = "Now saving frames for {} Hz target frequency".format(tf)
        displayText(currTF, win, 1.0)

        ###Save frames 
        saveFlickerFrames(FREQUENCIES,refresh_rate,tf,win, 3.0)

###Display text, fixation cross and stimulus frequency tf
def textCrossFlickerFreq(FREQUENCIES, refresh_rate, tf, win, mrk_outlet, time_dur = [1.0,1.0,5.0]):

    #Display text for 1.0 s
    displayText('Now displaying: {} Hz stimulus frequency'.format(str(tf)), win,  time_dur[0])

    ###Display fixation cross for 1.0 s 
    drawFixationCross(win,  time_dur[1])
    
    ###Display flickering stimulus for 5.0s and send event marker to start recording
    mrk_outlet.push_sample([str(tf) + 'Hz'])
    drawFlickeringStim(FREQUENCIES, refresh_rate, tf, win, time_dur[2])
    mrk_outlet.push_sample(['end_s'])
    drawBlankScreen(win, 1.0)

######################## MULTI-PATTERN RELATED FUNCTIONS FOR ONLINE SSVEP EXPERIMENTS ######################## 

##Convert seconds to frames 
def convertTimetoFrames(refresh_rate, time_dur):
    time_ms = time_dur*1000; 

    frame_dur = 1000/refresh_rate
    return np.round(time_ms/frame_dur).astype(int)

###Get positions for N stimulus flickers 
def getStimPositions(num_stim):

    ##LTRD
    left =  [-450, 0]
    top =   [0, 250]
    right = [450, 0]
    down =  [0,-250]

    ###Targets are always set in clock-wise fashion starting from the leftmost (or) top element
    stimPos = {2:[top,down], 
               3:[left, top, right], 
               4:[left, top, right, down]}
    
    return stimPos[num_stim]

###Get array of base flickering stimuli (white squares) 
def getBaseElementStimArray(my_win, num_targets, pos):
    return visual.ElementArrayStim(my_win, units = 'pix', nElements = num_targets, 
                                   xys = pos, colors = [-1.0, -1.0, -1.0], sizes = 150, opacities = 1, elementTex = None, 
                                   elementMask = None)

###Get on-off frame patterns for any target combination 
def getMultPattern(refresh_rate, targets):
    patternDict = {};

    for tf in targets:
        frame_dur = sum(getOnOffPatternDurations(refresh_rate,tf))
        patt = []

        for f in range(frame_dur):
            patt.append(1.0) if f % frame_dur < np.floor(frame_dur/2) else patt.append(-1.0)

        patternDict[tf] = (len(patt), patt)

    return patternDict

###Unpack pattern dictionary to the form [(frame_dur1, [pattern1])... (frame_durN, [patternN])]
def unpack(targets,patternDict):
    patts = []
    
    for tf in targets:
        patts.append(patternDict[tf])

    return patts

###Get color pattern from unpacked multipattern dictionary
def getColor(frame, patts):
    return [[c[1][frame%c[0]]] for c in patts]

##Draw multiple flickering stimuli to screen 
def drawMultipleFlicker(FREQUENCIES, my_win, refresh_rate, targets, time_dur = 600.0):

    ###Get number of stimulus targets
    num_targets = len(targets)
    if num_targets >= 2 and num_targets <= 4:
        for tf in targets:
            if(tf not in getValidFrequencies(refresh_rate)):
                print("Cannot display this flickering stimulus at {} Hz refresh rate".format(refresh_rate));
                return False
    
        ###Get positions for each stimulus and array of patterns to draw
        pos = getStimPositions(num_targets) 
        multPatt = unpack(targets, getMultPattern(refresh_rate, targets))
        arrayStim = getBaseElementStimArray(my_win, num_targets, pos)

        ###Begin Stimulus
        noFrames = convertTimetoFrames(refresh_rate, time_dur)

        for frame in range(noFrames):
            arrayStim.colors = getColor(frame, multPatt)
            arrayStim.draw(my_win)

            my_win.flip()
    else:
        print("Cannot display less than 2 or more than 4 stimuli")
        return False
