import pandas as pd
import numpy as np
import matplotlib.pyplot as plt 

####Load CSV files 
flicker_7_5Hz = pd.read_csv('./7_5Hz.csv') 
flicker_7_5Hz['timestamp'] = flicker_7_5Hz['timestamp'] - flicker_7_5Hz['timestamp'][0]
print(flicker_7_5Hz.head(17))

flicker_10Hz = pd.read_csv('./10Hz.csv') 
flicker_10Hz['timestamp'] = flicker_10Hz['timestamp'] - flicker_10Hz['timestamp'][0]
print(flicker_10Hz.head(10))

####Plot flickers to matplotlib 
def plotScreenFlicker(frequency, df, no_values, line_color):
    plt.plot(df['timestamp'][:no_values], df['value'][:no_values], color = line_color)
    plt.title('Screen flicker at ' + str(frequency) + 'Hz') 
    plt.xlabel('Time')
    plt.ylabel('Pattern')
    plt.grid(True, which = 'both')
    plt.show()

plotScreenFlicker(7.5, flicker_7_5Hz,50, 'blue')
plotScreenFlicker(10, flicker_10Hz,50, 'red')


