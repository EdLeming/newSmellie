# Test the SMELLIE laser keepalive
# functions to test the functionality of the interlock control code
# Test with superK GUI open, watch interlock status reported on gui

import logging, time, datetime
from smellie import interlock, superk_driver
from smellie.smellie_logger import SMELLIELogger

class InterlockTest(object):
    def __enter__(self):
        """
        Open the hardware required for tests.
        """
        global logging
        logging.debug("Open device.")
        self.il = interlock.Interlock()
        self.sk = superk_driver.SuperKDriver()
        #open device
        self.il.port_open()
        self.sk.port_open()

    def __exit__(self, type, value, traceback):
        """
        Close the hardware.
        """
        global logging
        logging.debug("Close device.")
        #close device
        self.il.port_close()
        self.sk.port_close()

    def test1(self):
        """
        Test current state & disarm (watch status quickly flash on & off)
        """
        global logging, npass, nfail
        
        #Firstly, test current state. (in turn tests many of the getter functions).
        logging.debug( "Test0: Current state: {}".format(self.il.current_state()))
        
        #test disarm (watch status quickly flash on & off)
        logging.debug("Test1: Send Arm then a Disarm")
        logging.debug("    Send arm: {}".format(self.il.set_arm()))
        logging.debug("    Send dis-arm: {}".format(self.il.set_disarm()))
        status = self.il.lasers_are_locked()
        logging.debug("    Check status (should be locked): {} (locked={})".format(self.il.get_status(), status))
        if (status==True): #disarmed = locked = relay contacts open = True
            logging.debug("Test PASSED")
            npass+=1
        else: 
            logging.debug("Test FAILED")
            nfail+=1
            
    def test2(self):
        """
        Test arm timeout
        """
        global logging, npass, nfail
        #test arm timeout
        logging.debug("Test2: Sending Arm and waiting for time-out (no keepalive sent)")
        logging.debug("    First arm: {}".format(self.il.set_arm()))
        status = self.il.lasers_are_locked()
        logging.debug("    Wait 1.2 seconds") #just enough time for keepalive to timeout. Slightly more than required. Exact time will cause error if serial is part-way through a readline
        time.sleep(1.2)
        status2 = self.il.lasers_are_locked()
        logging.debug("    Test status (should be locked): {} (locked={})".format(self.il.get_status(), status2))
        time.sleep(1.5) #ensure timed out for next test
        if (status==False and status2==True): 
            logging.debug("Test PASSED")
            npass+=1
        else: 
            logging.debug("Test FAILED")
            nfail+=1

    def test3(self):
        """
        Test sending keepalive
        """
        global logging, npass, nfail            
        #test sending keepalive
        logging.debug("Test3: Sending Arm with keep alive @ 1Hz: {}".format(self.il.set_arm()))
        status = self.il.lasers_are_locked()
        pulses = 0
        while (pulses < 5):
            pulses+=1
            logging.debug("    Test keep alive pulse {}".format(pulses))
            self.il.send_keepalive()
            time.sleep(1.0)
        status2 = self.il.lasers_are_locked()
        logging.debug("    Locked after keepalive pulses? (should be unlocked): {} (locked={})".format(self.il.get_status(), status2))
        time.sleep(1.5) #ensure timed out for next test
        if (status==False and status2==False): 
            logging.debug("Test PASSED")
            npass+=1
        else: 
            logging.debug("Test FAILED")
            nfail+=1

    def test4(self):
        """
        Test the status of the interlock as seen by the laser
        """
        global logging, npass, nfail            
        #test sending keepalive
        logging.debug("Test4: Test status via laser")
        logging.debug("    First arm: {}".format(self.il.set_arm()))
        status = self.il.lasers_are_locked()
        status2 = self.sk.is_interlock_locked()
        logging.debug("    Check status via SuperK laser (should be unlocked): Locked={}".format(status2))
        logging.debug("    And disarm: {}".format(self.il.set_disarm()))
        status3 = self.il.lasers_are_locked()
        status4 = self.sk.is_interlock_locked()
        logging.debug("    Check status via SuperK laser (should be locked): Locked={}".format(status4))
        if (status == False and status==status2 and status3==True and status3==status4): 
            logging.debug("Test PASSED")
            npass+=1
        else:
            logging.debug("Test FAILED")
            nfail+=1

#setup python logger
logging.basicConfig(filename='C:/SMELLIE/logs/testing/test_interlock.log', filemode="a", level=logging.DEBUG)
console = logging.StreamHandler() #print logger to console
console.setLevel(logging.DEBUG)
logging.getLogger('').addHandler(console)
logging.debug( "Begin Testing SMELLIE Interlock. {}".format( datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') ) )
SMELLIELogger.new_logger("test") #give SMELLIE logger a name
npass = 0
nfail = 0

interlock_test = InterlockTest()
with interlock_test:
    try:
        #test current state and disarm ability
        interlock_test.test1()
        #test arm timeout
        interlock_test.test2()
        #test sending keepalive
        interlock_test.test3()
        #test status as seen by laser (SuperK)
        interlock_test.test4()
    except Exception as e:
        logging.debug( "Exception: {}".format(e) )
    
logging.debug( "Finished Testing SMELLIE Interlock, pass: {}/{}, fail:{}/{}".format(npass,npass+nfail,nfail,npass+nfail) )
