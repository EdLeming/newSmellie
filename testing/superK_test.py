# Test the SMELLIE SuperK laser
# functions to test the functionality of the SuperK control code
# Monitor test with the spectrometer (or, alternatively the power meter)

import logging, time, datetime
from smellie import superk_driver, fibre_switch, ni_trigger_generator
from smellie.smellie_logger import SMELLIELogger

class SKTest(object):
    def __enter__(self):
        """
        Open the hardware required for tests.
        """
        global logging
        logging.debug("Open devices and record current settings:")
        
        self.fs = fibre_switch.FibreSwitch()
        self.ni = ni_trigger_generator.TriggerGenerator()
        self.sk = superk_driver.SuperKDriver()
        
        #open device
        self.sk.port_open()
        self.fs.port_open()
        
        #record original settings
        self.wavelength_low_original, self.wavelength_high_original = self.sk.get_wavelengths()
        
        #record original settings
        self.fs_original = self.fs.get_global_channel_number()
        logging.debug( "    Fibre switch channel: {}".format(self.fs_original))
        self.fs.set_io_channel_numbers(5,14) #superK fibre switch input 5. Power meter is output 14 (this is global channel 70)
        self.fs_channel = self.fs.get_global_channel_number()
        logging.debug( "    Set Fibre switch chan: {}".format(self.fs_channel))

    def __exit__(self, type, value, traceback):
        """
        Close the hardware. Ensure the settings have been reset.
        """
        global logging, npass, nfail
        logging.debug("Close devices and restore original settings (restored/original):")
        
        #restore original settings        
        self.fs_restored = self.fs.get_global_channel_number()
        if (self.fs_restored!=self.fs_original):
            self.fs.set_global_active_channel_number(self.fs_original)
            self.fs_restored = self.fs.get_global_channel_number()
            
        self.wavelength_low_restored, self.wavelength_high_restored = self.sk.get_wavelengths()
        if (self.wavelength_low_restored!=self.wavelength_low_original or self.wavelength_high_restored!=self.wavelength_high_original):
            self.sk.set_wavelengths(self.wavelength_low_original, self.wavelength_high_original)
            self.wavelength_low_restored, self.wavelength_high_restored = self.sk.get_wavelengths()

        #results
        logging.debug( "    SuperK wavelengths: {}/{} {}/{}".format(self.wavelength_low_original,self.wavelength_low_original,self.wavelength_high_original,self.wavelength_high_original))
        logging.debug( "    Fibre switch channel: {}/{}".format(self.fs_restored,self.fs_original))
        if (self.wavelength_low_restored==self.wavelength_low_original and self.wavelength_high_restored==self.wavelength_high_original and self.fs_original==self.fs_restored):
            logging.debug("Restore Settings PASSED")
            npass+=1
        else:
            logging.debug("Restore Settings FAILED")
            nfail+=1

        logging.debug("Close device.")
        #close device
        self.fs.port_close()
        self.sk.port_close()

    def test1(self):
        """
        Test current state & disarm (watch status quickly flash on & off)
        """
        global logging, npass, nfail
        
        #Firstly, test current state. (in turn tests many of the getter functions).
        logging.debug( "Test0: Current state: {}".format(self.sk.current_state()))
        
        if (True):
            logging.debug("Test1 PASSED")
            npass+=1
        else:
            logging.debug("Test1 FAILED")
            nfail+=1
    
    def test2(self):
        """
        Test2: Turn ready state (lock and emission) on and off
        """
        global logging, npass, nfail
        
        if (True):
            logging.debug("Test1 PASSED")
            npass+=1
        else:
            logging.debug("Test1 FAILED")
            nfail+=1
        
    def test3(self):
        """
        Test3: Move wavelengths
        """
        global logging, npass, nfail
        
        if (True):
            logging.debug("Test1 PASSED")
            npass+=1
        else:
            logging.debug("Test1 FAILED")
            nfail+=1
        
    def test4(self):
        """
        Test Fire laser (recieve triggers)
        """
        global logging, npass, nfail
        #Test4: Fire laser (recieve triggers)
   
        if (True):
            logging.debug("Test1 PASSED")
            npass+=1
        else:
            logging.debug("Test1 FAILED")
            nfail+=1

#setup python logger            
logging.basicConfig(filename=r'C:/SMELLIE/logs/testing/test_superk.log', filemode="a", level=logging.DEBUG)
console = logging.StreamHandler() #print logger to console
console.setLevel(logging.DEBUG)
logging.getLogger('').addHandler(console)
logging.debug( "Begin Testing SMELLIE SuperK laser driver. {}".format( datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') ) )
SMELLIELogger.new_logger("test") #give SMELLIE logger a name 
npass = 0
nfail = 0

sk_test = SKTest()
with sk_test:
    try:
        pass #test ability to set into ready mode and restore safe mode
        #sk_test.test1()
        #test firing pulses (while monitoring the power meter)
        #sk_test.test2()
    except Exception as e:
        logging.debug( "Exception: {}".format(e))
#results
logging.debug( "Finished Testing SMELLIE PQ laser driver test. pass: {}/{}, fail:{}/{}".format(npass,npass+nfail,nfail,npass+nfail) )
