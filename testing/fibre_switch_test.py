# Test the SMELLIE fibre switch
# functions to test the functionality of all the fibre switch control code
# Test while pulsing laser and monitoring fibre_switch output with power meter

import logging, time, datetime, random
from smellie import fibre_switch
from smellie.smellie_logger import SMELLIELogger

class FibreSwitchTest(object):
    def __enter__(self):
        """
        Open the hardware required for tests. Record setting which will be changed during testing.
        """
        global logging, npass, nfail
        logging.debug("Open devices and record current settings:")
        
        self.fs = fibre_switch.FibreSwitch()
        
        #open devices
        self.fs.port_open()
        
        #record original settings
        self.fs_original = self.fs.get_global_channel_number()
        logging.debug( "    Fibre switch channel: {}".format(self.fs_original))

    def __exit__(self, type, value, traceback):
        """
        Close the hardware. Ensure the settings have been reset.
        """
        global logging, npass, nfail
        logging.debug("Close devices and restore original settings (restored/original):")
        
        #restore original settings        
        self.fs_restored = self.fs.get_global_channel_number()
        if (self.fs_restored!=self.fs_original):
            self.fs.set_global_channel_number(self.fs_original)
            self.fs_restored = self.fs.get_global_channel_number()
            
        #results
        logging.debug( "    Fibre switch channel: {}/{}".format(self.fs_restored,self.fs_original))
        if (self.fs_original==self.fs_restored):
            logging.debug("Restore Settings PASSED")
            npass+=1
        else:
            logging.debug("Restore Settings FAILED")
            nfail+=1
        
        #close devices
        self.fs.port_close()

    def test1(self):
        """
        Test setting a channel.
        """
        global logging, npass, nfail
        #test current state. (in turn tests many of the getter functions).
        logging.debug( "    Current state: {}".format(self.fs.current_state()))
        
        #test setting channel (to random channel)
        chan_random = random.randint(1,70)
        if (self.fs_original==chan_random): 
            chan_random = random.randint(1,70)

        self.fs.set_global_channel_number(chan_random)
        chan_new = self.fs.get_global_channel_number()
        logging.debug( "Test setting channel: set={}, get={}".format(chan_random, chan_new))

        #result
        if (chan_random==chan_new and chan_random!=self.fs_original): 
            logging.debug("Test PASSED")
            npass+=1
        else: 
            logging.debug("Test FAILED")
            nfail+=1

#setup python logger
logging.basicConfig(filename='C:/SMELLIE/logs/testing/test_fibre_switch.log', filemode="a", level=logging.DEBUG)
console = logging.StreamHandler() #print logger to console
console.setLevel(logging.DEBUG)
logging.getLogger('').addHandler(console)
logging.debug( "Begin Testing SMELLIE Fibre Switch. {}".format( datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') ) )
SMELLIELogger.new_logger("test") #give SMELLIE logger a name 
npass = 0
nfail = 0

fibre_switch_test = FibreSwitchTest()
with fibre_switch_test:
    try:
        #test ability to set (and get) a channel
        fibre_switch_test.test1()
    except Exception as e:
        logging.debug( "Exception: {}".format(e) )
    
logging.debug( "Finished Testing SMELLIE Fibre Switch, pass: {}/{}, fail:{}/{}".format(npass,npass+nfail,nfail,npass+nfail) )
    
