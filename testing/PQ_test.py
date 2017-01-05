# Test the SMELLIE PicoQuant laser controller (SEPIA)
# Sets up a laser in master mode. Uses NI to pulse it.

import logging, time, datetime
from smellie import pq_driver, fibre_switch, laser_switch, ni_trigger_generator
from smellie.smellie_logger import SMELLIELogger

class PQTest(object):
    def __enter__(self):
        """
        Open the hardware required for tests. Record setting which will be changed during testing.
        """
        global logging, npass, nfail
        logging.debug("Open devices and record current settings:")
        
        self.pq = pq_driver.PQDriver()
        self.ni = ni_trigger_generator.TriggerGenerator()
        self.fs = fibre_switch.FibreSwitch()
        self.ls = laser_switch.LaserSwitch()
        
        #check laser switch channel (before opening PQ laser incase we need to switch lasers which requires PQ to disconnect..)
        self.ls_original = self.ls.get_active_channel()
        logging.debug( "    Laser switch channel: {}".format(self.ls_original))
        if (self.ls_original == 0 or self.ls_original ==5):
            self.ls.set_active_channel(3)
            self.ls_channel = self.ls.get_active_channel()
            logging.debug( "    Set laser switch channel: {}".format(self.ls_channel))
        else:
            self.ls_channel = self.ls_original
        
        #open devices
        self.pq.port_open()
        self.pq.go_safe()
        #no close for laser switch
        self.fs.port_open()
        
        #record original settings
        self.fs_original = self.fs.get_global_channel_number()
        logging.debug( "    Fibre switch channel: {}".format(self.fs_original))
        self.fs.set_io_channel_numbers(self.ls_channel,14)
        self.fs_channel = self.fs.get_global_channel_number()
        logging.debug( "    Set Fibre switch chan: {}".format(self.fs_channel))
        
    def __exit__(self, type, value, traceback):
        """
        Close the hardware. Ensure the settings have been reset.
        """
        global logging, npass, nfail
        logging.debug("Close devices and restore original settings (restored/original):")
        
        #reset to safe mode
        self.pq.go_safe()
        
        #restore original settings        
        self.fs_restored = self.fs.get_global_channel_number()
        if (self.fs_restored!=self.fs_original):
            self.fs.set_global_active_channel_number(self.fs_original)
            self.fs_restored = self.fs.get_global_channel_number()

        self.ls_restored = self.ls.get_active_channel()
        if (self.ls_restored!=self.ls_original):
            self.ls.set_active_channel(self.ls_original)
            self.ls_restored = self.ls.get_active_channel()

        #results
        logging.debug( "    Laser switch channel: {}/{}".format(self.ls_restored,self.ls_original))
        logging.debug( "    Fibre switch channel: {}/{}".format(self.fs_restored,self.fs_original))
        if (self.ls_original==self.ls_restored and self.fs_original==self.fs_restored):
            logging.debug("Restore Settings PASSED")
            npass+=1
        else:
            logging.debug("Restore Settings FAILED")
            nfail+=1

        #close devices
        self.pq.port_close()
        #no close for laser switch
        self.fs.port_close()

    def test1(self):
        """
        Test setting the laser to ready mode and restoring safe mode. The interlock should be unlocked for this.
        """
        global logging, npass, nfail
        logging.debug("Run test 1.")
        intensity = 1000
        
        #print current state. (in turn tests many of the getter functions).
        logging.debug( "    Current state: {}".format( self.pq.current_state() ) )

        self.pq.go_safe()
        locked_safe = self.pq.is_soft_lock_on()
        intensity_safe = self.pq.get_intensity()
        logging.debug("    Safe mode: Locked={}, Intensity={}".format(locked_safe,intensity_safe))
        
        self.pq.go_ready(intensity)
        locked_ready = self.pq.is_soft_lock_on()
        intensity_ready = self.pq.get_intensity()
        logging.debug("    Ready mode: Locked={}, Intensity={}".format(locked_ready,intensity_ready))
        
        self.pq.go_safe()
        locked_restored = self.pq.is_soft_lock_on()
        intensity_restored = self.pq.get_intensity()

        if (locked_safe == True and intensity_safe == 0 and locked_ready == False and intensity_ready == intensity and locked_restored==locked_safe and intensity_restored==intensity_safe and locked_safe!=locked_ready and intensity_safe!=intensity_ready):
            logging.debug("Test1 PASSED")
            npass+=1
        else:
            logging.debug("Test1 FAILED")
            nfail+=1
        
    def test2(self):
        """
        Test firing the current laser. Use while monitoring the power meter (checks to see if fibre switch is set to the correct output fibre)
        """
        global logging, npass, nfail
        logging.debug("Run test 2.")
        trig_npulses = 3000
        trig_rate = 1000
        intensity = 1000

        if (self.fs_channel!=14 and self.fs_channel!=28 and self.fs_channel!=42 and self.fs_channel!=56):
            raise Exception("Fibre switch not set to power meter fibre. Are you sure you want to fire into the detetor?")
            logging.debug("Test2 FAILED")
            nfail+=1
        elif (self.ls_channel==0 or self.ls_channel == 5):
            logging.debug("Test2 FAILED")
            nfail+=1
            raise Exception("Laser switch not set to a PQ laser")
        else:  
            self.pq.go_ready(intensity)
            logging.debug('    Triggers Begin. pulses={}, rate={}, intensity={}'.format(trig_npulses, trig_rate, intensity))
            self.ni.generate_triggers(trig_npulses,trig_rate,'PQ')
            self.pq.go_safe();
            logging.debug("    Triggers Finished.")
            logging.debug("Test2 PASSED")
            npass+=1

#setup python logger            
logging.basicConfig(filename=r'C:/SMELLIE/logs/testing/test_PQ.log', filemode="a", level=logging.DEBUG)
console = logging.StreamHandler() #print logger to console
console.setLevel(logging.DEBUG)
logging.getLogger('').addHandler(console)
logging.debug( "Begin Testing SMELLIE PQ laser driver. {}".format( datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') ) )
SMELLIELogger.new_logger("test") #give SMELLIE logger a name 
npass = 0
nfail = 0

pq_test = PQTest()
with pq_test:
    try:
        #test ability to set into ready mode and restore safe mode
        pq_test.test1()
        #test firing pulses (while monitoring the power meter)
        pq_test.test2()
    except Exception as e:
        logging.debug( "Exception: {}".format(e))
#results
logging.debug( "Finished Testing SMELLIE PQ laser driver test. pass: {}/{}, fail:{}/{}".format(npass,npass+nfail,nfail,npass+nfail) )
