# Test the SMELLIE PicoQuant (PQ) lasers
# Runs an intensity scan of each laser and saves to file (so also uses laser switch, fibre switch, powermeter).
# Uses the lasers internal 2.5MHz trigger.

import logging, time, datetime, numpy
from smellie import laser_driver, power_meter, fibre_switch, laser_switch
from sepia.slm import get_pulse_parameters, set_pulse_parameters, decode_freq_trig_mode
from smellie_config import LASER_DRIVER_SLOT_ID, LASER_DRIVER_DEV_ID, LASER_SLOT_ID

logging.basicConfig(filename=r'C:\SMELLIE\logs\test_PQ_intensity_scan_inttrigger.log', filemode="a", level=logging.DEBUG)
console = logging.StreamHandler() #print logger to console
console.setLevel(logging.DEBUG)
logging.getLogger('').addHandler(console)

try:
    ld = laser_driver.LaserDriver()
    fs = fibre_switch.FibreSwitch()
    ls = laser_switch.LaserSwitch()
    pm = power_meter.PowerMeter()
    
    logging.debug("Begin SMELLIE PQ laser intensity scan (internal 2.5MHz trigger). {}".format(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')))
    
    #open devices
    fs.port_open()
    pm.port_open()
 
    #record original settings
    ls_original = ls.get_active_channel()
    fs_original = fs.get_global_channel_number()
    pm_original = pm.get_wavelength()
    pm_avg_original = pm.get_average_count()
    
    logging.debug( "Current settings: Laser switch chan: {}, Fibre switch: {}".format(ls_original, fs_original))
    
    laser_numbers = range(1,5,1) #test lasers 1 thru 4
    wavelengths = (375, 407, 446, 495)

    power_meter_nsamples = 50
    power_meter_sample_rate = 10
    pm.set_average_count(3)
    
    #at 100% intensity @ 100kHz, Laser1(375nm): ~13nW, Laser2(407nm): ~424nW, Laser3(446nm): ~37nW, Laser4(495nm): ~915nW.

    for laser_number, wavelength in zip(laser_numbers,wavelengths):
        logging.debug( "Begin intensity scan of laser (internal 2.5MHz trigger): {} ({}nm)".format(  laser_number, wavelength))
        intensities = range(0,1010,50) #from 0 to 100% intensity in 1% steps
        powerMean = []
        powerSD = []
        powerRange = []
    
        ls.set_active_channel(laser_number)
        fs.set_io_channel_numbers(laser_number, 14) #output fibre 14 = powermeter
        logging.debug( "Setting: Laser Switch: {}, Fibre switch: {}".format( ls.get_active_channel(), fs.get_global_channel_number()))
        
        ld.port_open()
        time.sleep(5)
        ld.go_safe()
        ld.set_soft_lock(False)
        set_pulse_parameters(LASER_DRIVER_DEV_ID, LASER_SLOT_ID, 'INT') #set internal trigger, overriding safe mode.
        trig_rate = 2500000
        
        for intensity in intensities:
            ld.set_intensity(intensity)
            time.sleep(1)
            
            power_mean, power_sd, power_range = pm.get_mean_power(power_meter_nsamples,power_meter_sample_rate)
            powerMean.append( power_mean )
            powerSD.append( power_sd )
            powerRange.append( power_range )

            print "(laser, wavelength, intensity(%), power_mean(W), power_sd(W), power_range(W)): {}, {}, {}, {}, {}\n".format(laser_number, wavelength, intensity, power_mean, power_sd, power_range)
 
        #laser finished firing. Close (before disconnecting via fibre switch)
        ld.go_safe()
        ld.port_close()
        
        #write intensity vs power data to file
        fileOut = open(r'C:\SMELLIE\workDiary\test_PQ_intensity_scan_inttrigger_{}nm.dat'.format(wavelength), 'a')
        fileOut.write('Laser: {}, Wavelength(nm): {}, Repetition Rate: {}, Power meter sample average: {} \n'.format( laser_number, wavelength, trig_rate, power_meter_nsamples))
        fileOut.write('Intensity(%), Power_mean(W), Power_sd(W), Power_range(W)\n')
        for i,j,k,l in zip(intensities,powerMean,powerSD,powerRange):
            fileOut.write( '{},{},{},{}\n'.format( i,j,k,l ) )
        fileOut.closed
 
    #go back to safe, original states
    ls.set_active_channel(ls_original)
    fs.set_global_channel_number(fs_original)
    pm.set_wavelength(pm_original)
    pm.set_average_count(pm_avg_original)
    logging.debug( "Current settings (restored/original): Laser switch chan: {}/{}, Fibre switch: {}/{}, Power meter wavelength: {}/{} & Avg count: {}/{}".format( ls.get_active_channel(),ls_original, fs.get_global_channel_number(),fs_original,pm.get_wavelength(),pm_original, pm.get_average_count(),pm_avg_original))
    
    #close devices
    fs.port_close()
    pm.port_close()
    
    logging.debug( "Finished SMELLIE PQ laser intensity scan (internal 2.5MHz trigger). {}".format(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')))
    
except Exception, e:
    logging.debug("Exception:")
    logging.debug(e)

