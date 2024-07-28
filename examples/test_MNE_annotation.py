import pandas as pd 
import utilities.utilities as utils

marker_filepath = './trials/csv/all_targets.csv'
broadcast_marker = 'wait'; 
paradigm_onset_delay = 2.0

###Adding events to the raw object
markers = utils.createMarkerDF(marker_filepath, broadcast_marker, paradigm_onset_delay)
print(markers.head(10))

###Create annotations object from out marker dataframe
annot = utils.createAnnotationObject(markers, end_stim = 'end_s', end_exp = 'end', dev = True)

