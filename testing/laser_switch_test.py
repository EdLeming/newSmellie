# Test the SMELLIE laser switch
# functions to test the functionality of the laser switch control code
# Test while watching laser switch. (possibly with triggers and with powermeter? but ideally spectrometer)

import logging, time, datetime
from smellie import laser_switch
ls = laser_switch.LaserSwitch()

logging.basicConfig(filename='C:/SMELLIE/logs/test_laser_switch.log', filemode="a", level=logging.DEBUG)
console = logging.StreamHandler() #print logger to console
console.setLevel(logging.DEBUG)
logging.getLogger('').addHandler(console)

npass = 0
nfail = 0

try:

    logging.debug( "Begin Testing SMELLIE Laser Switch. {}".format( datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') ) )
    #test current state. (in turn tests many of the getter functions).
    logging.debug( "Current state: {}".format( ls.current_state() ) )

    #test set channel
    time.sleep(1)
    chan_original = ls.get_active_channel()
    
    if (chan_original>=0 and chan_original<=4): ls.set_active_channel(chan_original+1)
    elif (chan_original==5): ls.set_active_channel(chan_original-1)
    else: logging.debug( "Error testing set channel")
    chan_new = ls.get_active_channel()
    logging.debug( "Test setting channel: {}, ('selected' state: {})".format( chan_new, ls.get_selected_channel() ) )
    
    #set back to original channel
    ls.set_active_channel(chan_original)
    chan_restored = ls.get_active_channel()
    logging.debug( "Restore original channel: {}, ('selected' state: {})".format(  chan_restored, ls.get_selected_channel() ) )
    
    if (chan_restored==chan_original and chan_new!=chan_original): 
        logging.debug("Test PASSED")
        npass+=1
    else: 
        logging.debug("Test FAILED")
        nfail+=1
    
    logging.debug( "Finished Testing SMELLIE Laser Switch, pass: {}/{}, fail:{}/{}".format(npass,npass+nfail,nfail,npass+nfail) )
    
except Exception, e:
    logging.debug( "Exception:" )
    logging.debug( e )