# Test the SMELLIE PicoQuant (PQ) lasers
# Sets up laser in master mode state. Use NI (somehow else) to pulse it.

import logging, time, datetime
from smellie import laser_driver, fibre_switch, laser_switch, ni_trigger_generator

logging.basicConfig(filename=r'C:\SMELLIE\logs\test_PQ_switch.log', filemode="a", level=logging.DEBUG)
console = logging.StreamHandler() #print logger to console
console.setLevel(logging.DEBUG)
logging.getLogger('').addHandler(console)

npass = 0
nfail = 0

try:

    ld = laser_driver.LaserDriver()
    fs = fibre_switch.FibreSwitch()
    ls = laser_switch.LaserSwitch()
    ni = ni_trigger_generator.TriggerGenerator()
    
    logging.debug( "Begin SMELLIE PQ laser switch test. {}".format( datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') ) )
    
    #open devices
    fs.port_open()
    ld.port_open()
    ld.go_safe()
 
    #record original settings
    ls_original = ls.get_active_channel()
    fs_original = fs.get_global_channel_number()
    
    logging.debug( "Current settings: Laser switch chan: {}, Fibre switch: {}".format( ls_original, fs_original ) )
    
    laser_numbers = range(1,5,1) #test lasers 1 thru 4
    wavelengths = (375, 407, 446, 495)
    trig_npulses = 300000
    trig_rate = 100000 # at 100% intensity @ 100kHz, Laser1(375nm): ~13nW, Laser2(407nm): ~424nW, Laser3(446nm): ~37nW, Laser4(495nm): ~915nW.
    intensity = 1000

    for laser_number, wavelength in zip(laser_numbers,wavelengths):
    
        logging.debug( "Setting Laser switch chan: {}, Fibre switch: {}".format( ls.get_active_channel(), fs.get_global_channel_number() ) ) 
        ld.port_close() #close Sepia before laser switch d/c it.
        ls.set_active_channel(laser_number)
        fs.set_io_channel_numbers(laser_number, 14) #output fibre 14 = power , not used here, but detector-safe.
        
        ld.port_open()
        ld.go_safe()
        ld.set_soft_lock(False)
        ld.set_intensity(intensity)
        
        logging.debug('Triggers Begin. pulses={}, rate= {}'.format(trig_npulses, trig_rate))
        ni.generate_triggers(trig_npulses,trig_rate,'PQ')
        logging.debug("Triggers Finished.")
 

    ld.go_safe()
    ls.set_active_channel(ls_original)
    fs.set_global_channel_number(fs_original)
    ls_restored = ls.get_active_channel()
    fs_restored = fs.get_global_channel_number()
    logging.debug( "Current settings (restored/original): Laser switch chan: {}/{}, Fibre switch: {}/{}".format( ls_restored,ls_original, fs_restored,fs_original ) )

    #results
    if (ls_original==ls_restored and fs_original==fs_restored):
        logging.debug("Test PASSED")
        npass+=1
    else:
        logging.debug("Test FAILED")
        nfail+=1
    
    #close devices
    ld.port_close()
    fs.port_close()

    logging.debug( "Finished SMELLIE PQ laser switch test. pass: {}/{}, fail:{}/{}".format(npass,npass+nfail,nfail,npass+nfail) )

except Exception, e:
    logging.debug( "Exception:" )
    logging.debug( e )
    
