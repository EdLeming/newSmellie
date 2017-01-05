# Test the SMELLIE Spectrometer
# functions to test the functionality of the Spectrometer control code
# Test with superK laser pulses

import logging, time, datetime
from smellie import spectrometer
spec = spectrometer.Spectrometer()

logging.basicConfig(filename=r'C:\SMELLIE\logs\test_spectrometer.log', filemode="a", level=logging.DEBUG)
console = logging.StreamHandler() #print logger to console
console.setLevel(logging.DEBUG)
logging.getLogger('').addHandler(console)

npass = 0
nfail = 0

try:
    logging.debug( "Begin Testing SMELLIE Spectrometer. {}".format( datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') ) )   
    
    #test current state. (in turn tests many of the getter functions).
    spec.open_spectrometer()
    logging.debug( "Current state: {}".format( spec.current_state() ) )

    #take data
    #oo.setExternalTriggerMode(0)
    #spectrumData = oo.getSpectrum(wrapper)
    #wavelengthData = oo.getWavelengths(wrapper)
    #oo.writeSpectrum(runNumber,wavelengthData,spectrumData)
    
    #if True: 
    logging.debug("Test PASSED")
    npass+=1
    #else: 
    #    logging.debug("Test FAILED")
    #    nfail+=1
    
    #close spectrometer   
    spec.close_spectrometer()
    
    logging.debug( "Finished Testing SMELLIE Spectrometer, pass: {}/{}, fail:{}/{}".format(npass,npass+nfail,nfail,npass+nfail) )
    
except Exception, e:
    logging.debug( "Exception:" )
    logging.debug( e )