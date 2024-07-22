import psychopy.visual as visual
import psychopy.core  as core
import numpy as np

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

def getValidFrequencies(refresh_rate):
    if refresh_rate == 60:
        return [6.66, 7.5, 8.57, 10, 12, 15]

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
        

## Display flickering stimulus to screen 
def drawFlickeringStim(FREQUENCIES, refresh_rate, frequency, my_win, time_dur):
    if(refresh_rate == 60):
        if(frequency not in FREQUENCIES):
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

    if(refresh_rate == 60):
        if(tf not in FREQUENCIES):
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
    
####Write frame screenshots for all target frequencies 
def saveAllFrames(FREQUENCIES):
    win = createWindow(1,800,600,True,[0,0,0],'pyglet');
    refresh_rate = 60;

    for tf in FREQUENCIES:

        ###Display text to indicate current target frequency     
        currTF = "Now saving frames for {} Hz target frequency".format(tf)
        displayText(currTF, win, 1.0)

        ###Save frames 
        saveFlickerFrames(FREQUENCIES,refresh_rate,tf,win, 3.0)

