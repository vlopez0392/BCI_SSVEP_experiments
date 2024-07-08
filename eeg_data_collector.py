from pylsl import StreamInlet, resolve_stream

####Takeoff and landing marker stream
mrk_info = resolve_stream('name', 'takeoff_landing')
print("Looking for takeoff marker stream...")
mrk_in = StreamInlet(mrk_info[0])
takeoff_t = None
land_t = None
paradigm_Done = False

####Offline data collection 
while True:
    mrk, t_mrk = mrk_in.pull_sample() ###Make operation non-blocking with timeout = 0

    if mrk[0] == 'takeoff':
        takeoff_t = t_mrk
        print('takeoff_initiated at time ' + str(t_mrk))
        print("Looking for landing marker stream...")

    if mrk[0] == 'landing':
        land_t = t_mrk
        print('Landing_initiated at time ' + str(t_mrk))
        print("Approximate time difference between markers: " + str((land_t - takeoff_t)) + '\n')

    if mrk[0] == 'end':
       print("Paradigm marker end at " + str(t_mrk))
       break
    