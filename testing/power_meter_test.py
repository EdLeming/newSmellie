# Test the SMELLIE Power Meter
# functions to test the functionality of the laser switch control code
# Test with a laser into fibre switch (5,14)

import logging, time, datetime
from smellie import power_meter
pm = power_meter.PowerMeter()

logging.basicConfig(filename='C:\SMELLIE\logs\test_power_meter.log', filemode="a", level=logging.DEBUG)
console = logging.StreamHandler() #print logger to console
console.setLevel(logging.DEBUG)
logging.getLogger('').addHandler(console)

npass = 0
nfail = 0

try:

    logging.debug( "Begin Testing SMELLIE Power Meter. {}".format( datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') ) ) 

    #open USB connection
    pm.port_open()  
    
    #test current state.
    logging.debug( "Current state: {}".format( pm.current_state() ) )

    if type(pm.get_power()) == float: 
        logging.debug("Test PASSED")
        npass+=1
    else: 
        logging.debug("Test FAILED")
        nfail+=1
    
    ## test2 set wavelength    
    wave_original = pm.get_wavelength()
    
    if (wave_original>=300 and wave_original<=999): pm.set_wavelength(wave_original+10)
    elif (wave_original==1000): pm.set_wavelength(wave_original-10)
    else: logging.debug( "Error testing set wavelength")
    wave_new = pm.get_wavelength()
    logging.debug( "Test setting wavelength: {}".format(wave_new) )
    
    #set back to original channel
    pm.set_wavelength(wave_original)
    wave_restored = pm.get_wavelength()
    logging.debug( "Restore original channel: {}".format(wave_restored) )
    
    if (wave_restored==wave_original and wave_new!=wave_original): 
        logging.debug("Test PASSED")
        npass+=1
    else: 
        logging.debug("Test FAILED")
        nfail+=1
    
    #close USB connection
    pm.port_close()
    
    logging.debug( "Finished Testing SMELLIE Power Meter, pass: {}/{}, fail:{}/{}".format(npass,npass+nfail,nfail,npass+nfail) )
    
except Exception, e:
    logging.debug( "Exception:" )
    logging.debug( e )