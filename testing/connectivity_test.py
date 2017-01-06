# Test connection to SMELLIE hardware
# functions to test if a connection can be made to each piece of equipment

import logging, time, datetime
from smellie import laser_switch, ni_trigger_generator, fibre_switch, pq_driver, interlock, power_meter, superk_driver, spectrometer
from smellie.smellie_logger import SMELLIELogger

class ConnectivityTest(object):
    def __enter__(self):
        """
        Open the hardware required for tests. Record setting which will be changed during testing.
        """
        global logging, npass, nfail
        logging.debug("Open devices.")
        
        self.ls = laser_switch.LaserSwitch()
        self.ni = ni_trigger_generator.TriggerGenerator()
        self.fs = fibre_switch.FibreSwitch()
        self.pq = pq_driver.PQDriver()
        self.il = interlock.Interlock()
        self.pm = power_meter.PowerMeter()
        self.sk = superk_driver.SuperKDriver()
        self.sp = spectrometer.Spectrometer()

    def __exit__(self, type, value, traceback):
        """
        Close the hardware. Ensure the settings have been reset.
        """
        global logging, npass, nfail
        logging.debug("Close devices.")
        
        #close devices. All throw exceptions as they should already be closed, so pass these exceptions.
        try:
            self.fs.port_close()
            self.il.port_close()
            self.pq.port_close()
            self.pm.port_close()
            self.sk.port_close() 
            self.sp.port_close()
        except (fibre_switch.FibreSwitchLogicError, 
                interlock.InterlockLogicError, 
                pq_driver.PQDriverLogicError,
                power_meter.PowerMeterLogicError,
                superk_driver.SuperKDriverLogicError,
                spectrometer.SpectrometerLogicError):
            pass

    def test1(self):
        """
        Test all without opening, should show disconnected (connected = False)
        The laser switch and NI DAQ don't have any connect/disconnect functions. They open automatically (cannot test false state).
        """
        global logging, npass, nfail
        #Test all without opening, should show disconnected (connected = False)
        #The laser switch and NI DAQ don't have any connect/disconnect functions. They open automatically (cannot test false state).
        logging.debug( "Testing disconnected states (connection = False):" )
        fsc = self.fs.is_connected()
        logging.debug( "Fibre Switch: {}".format( fsc ) )
        pqc = self.pq.is_connected()
        logging.debug( "PQ Lasers: {}".format( pqc ) )
        ilc = self.il.is_connected()
        logging.debug( "Interlock: {}".format( ilc ) )
        pmc = self.pm.is_connected()
        logging.debug( "Power Meter: {}".format( pmc ) )
        skc = self.sk.is_connected()
        logging.debug( "SuperK Laser: {}".format( skc ) )
        spc = self.sp.is_connected()
        logging.debug( "Spectrometer: {}".format( spc ) )
        
        if (fsc==False and pqc==False and ilc==False and pmc==False and skc==False and spc==False): 
            logging.debug("Test PASSED")
            npass+=1
        else: 
            logging.debug("Test FAILED")
            nfail+=1

    def test2(self):
        """
        Open (and close) all hardware and test if connection is successful.
        """
        global logging, npass, nfail
        #Now open (and close) all and test if connection is successful 
        logging.debug( "Testing connected states (True = connected):" )
        lsc = self.ls.is_connected()
        logging.debug( "Laser Switch: {}".format( lsc ) )
        
        nic = self.ni.is_connected()
        logging.debug( "NI DAQ: {}".format( nic ) )
        
        self.fs.port_open()
        fsc = self.fs.is_connected()
        logging.debug( "Fibre Switch: {}".format( fsc ) )
        self.fs.port_close()
        
        self.pq.port_open()
        pqc = self.pq.is_connected()
        logging.debug( "PQ Lasers: {}".format( pqc ) )
        self.pq.port_close()
        
        self.il.port_open()
        ilc = self.il.is_connected()
        logging.debug( "Interlock: {}".format( ilc ) )
        self.il.port_close()
        
        self.pm.port_open()
        pmc = self.pm.is_connected()
        logging.debug( "Power Meter: {}".format( pmc ) )
        self.pm.port_close()
        
        self.sk.port_open()
        skc = self.sk.is_connected()
        logging.debug( "SuperK Laser: {}".format( skc ) )
        self.sk.port_close()
        
        self.sp.port_open()
        spc = self.sp.is_connected()
        logging.debug( "Spectrometer: {}".format( spc ) )   
        self.sp.port_close()

        if (lsc==True and nic==True and fsc==True and pqc==True and ilc==True and pmc==True and skc==True and spc==True): 
            logging.debug("Test PASSED")
            npass+=1
        else: 
            logging.debug("Test FAILED")
            nfail+=1

#setup python logger
logging.basicConfig(filename='C:/SMELLIE/logs/testing/test_connectivity.log', filemode="a", level=logging.DEBUG)
console = logging.StreamHandler() #print logger to console
console.setLevel(logging.DEBUG)
logging.getLogger('').addHandler(console)
logging.debug( "Begin Testing SMELLIE equipment connection status: {}".format( datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') ) )  
SMELLIELogger.new_logger("test") #give SMELLIE logger a name 
npass = 0
nfail = 0

connectivity_test = ConnectivityTest()
with connectivity_test:
    try:
        #check to see the response when hardware isn't yet connected
        connectivity_test.test1()
        #connect hardware and check the response
        connectivity_test.test2()
    except Exception as e:
        logging.debug( "Exception: {}".format(e) )

logging.debug( "Finished Testing SMELLIE equipment connection status. pass: {}/{}, fail:{}/{}".format(npass,npass+nfail,nfail,npass+nfail) )
