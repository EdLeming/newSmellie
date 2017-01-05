# Test the SMELLIE NI trigger generator
# functions to test the functionality of the NI trigger generator control code
# Test while watching superK gui (shows trigger rate on gui)

import logging, time, datetime
from smellie import laser_switch
ls = laser_switch.LaserSwitch()

logging.basicConfig(filename='C:\SMELLIE\logs\test_ni_trigger_generator.log', filemode="a", level=logging.DEBUG)
console = logging.StreamHandler() #print logger to console
console.setLevel(logging.DEBUG)
logging.getLogger('').addHandler(console)

npass = 0
nfail = 0

try:

    logging.debug( "Begin Testing SMELLIE NI trigger generator. {}".format( datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') ) )   
    #test current state. (in turn tests many of the getter functions).
    logging.debug( "Current state: {}".format( ni.current_state() ) )

    #test set channel
    

    
    if (chan_restored==chan_original and chan_new!=chan_original): 
        logging.debug("Test PASSED")
        npass+=1
    else: 
        logging.debug("Test FAILED")
        nfail+=1
    
    logging.debug( "Finished Testing SMELLIE NI trigger generator, pass: {}/{}, fail:{}/{}".format(npass,npass+nfail,nfail,npass+nfail) )
    
except Exception, e:
    logging.debug( "Exception:" )
    logging.debug( e )