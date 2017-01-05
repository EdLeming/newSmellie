# Test the SMELLIE PicoQuant (PQ) lasers
# Runs an intensity scan of each laser and saves to file (so also uses laser switch, fibre switch, powermeter).

import logging, time, datetime, numpy
from multiprocessing.pool import ThreadPool
from smellie import laser_driver, power_meter, fibre_switch, laser_switch, ni_trigger_generator

def measure_power(nsamples,sample_rate):
    print "Power measurement begin."
    power_mean, power_sd, power_range = pm.get_mean_power(nsamples,sample_rate)
    print "Power measurement finished."
    return power_mean, power_sd, power_range

if __name__ == "__main__":

    logging.basicConfig(filename=r'C:\SMELLIE\logs\test_PQ_intensity_scan_nitrigger.log', filemode="a", level=logging.DEBUG)
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
        pm = power_meter.PowerMeter()
        pool = ThreadPool(processes=1)
        
        logging.debug( "Begin SMELLIE PQ laser intensity scan (default NI trigger). {}".format( datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') ) )
        
        #open devices
        fs.port_open()
        ld.port_open()
        pm.port_open()
        ld.go_safe()
     
        #record original settings
        ls_original = ls.get_active_channel()
        fs_original = fs.get_global_channel_number()
        pm_original = pm.get_wavelength()
        
        logging.debug( "Current settings: Laser switch chan: {}, Fibre switch: {}".format( ls_original, fs_original ) )
        
        laser_numbers = range(1,5,1) #test lasers 1 thru 4
        wavelengths = (375, 407, 446, 495)

        power_meter_nsamples = 5
        power_meter_sample_rate = 5
        measure_power_args = (power_meter_nsamples,power_meter_sample_rate) #(nsamples,rate)
        trig_npulses = 300000
        trig_rate = 100000 # at 100% intensity @ 100kHz, Laser1(375nm): ~13nW, Laser2(407nm): ~424nW, Laser3(446nm): ~37nW, Laser4(495nm): ~915nW.

        for laser_number, wavelength in zip(laser_numbers,wavelengths):

            logging.debug( "Begin intensity scan of laser: {} ({}nm)".format(  laser_number, wavelength ) )
            intensities = range(0,1010,50) #from 0 to 100% intensity in 5% steps
            powerMean = []
            powerSD = []
            powerRange = []

            ld.port_close() #close Sepia before laser switch d/c it.
            ls.set_active_channel(laser_number)
            fs.set_io_channel_numbers(laser_number, 14) #output fibre 14 = powermeter
            logging.debug( "Setting: Laser switch chan: {}, Fibre switch: {}".format( ls.get_active_channel(), fs.get_global_channel_number() ) )  

            ld.port_open()
            ld.go_safe()
            ld.set_soft_lock(False)
            
            for intensity in intensities:
                ld.set_intensity(intensity)
                
                async_measure_power = pool.apply_async(measure_power, measure_power_args)
                logging.debug('\nTriggers Begin. pulses={}, rate= {}'.format(trig_npulses, trig_rate))
                ni.generate_triggers(trig_npulses, trig_rate, 'PQ')
                logging.debug("\nTriggers Finished.")
                power_mean, power_sd, power_range = async_measure_power.get()
                powerMean.append( power_mean )
                powerSD.append( power_sd )
                powerRange.append( power_range )

                print "(laser, wavelength, intensity(%), power_mean(W), power_sd(W), power_range(W)): {}, {}, {}, {}, {}\n".format(laser_number, wavelength, intensity, power_mean, power_sd, power_range)
     
            fileOut = open(r'C:\SMELLIE\workDiary\test_PQ_intensity_scan_nitrigger_{}nm.dat'.format(wavelength), 'a')
            fileOut.write('Laser: {}, Wavelength(nm): {}, Repetition Rate: {}, Power meter sample average: {}\n'.format(laser_number, wavelength, trig_rate, power_meter_nsamples))
            fileOut.write('Intensity(%), Power_mean(W), Power_sd(W), Power_range(W)\n')
            for i,j,k,l in zip(intensities,powerMean,powerSD,powerRange):
                fileOut.write( '{},{},{},{}\n'.format( i,j,k,l ) )
            fileOut.closed
     
        #go back to safe, original states
        ld.go_safe()
        ls.set_active_channel(ls_original)
        fs.set_global_channel_number(fs_original)
        pm.set_wavelength(pm_original)
        ls_restored = ls.get_active_channel()
        fs_restored = fs.get_global_channel_number()
        pm_restored = pm.get_wavelength()
        logging.debug( "Current settings (restored/original): Laser switch chan: {}/{}, Fibre switch: {}/{}, Power meter wavelength: {}/{}".format( ls_restored,ls_original, fs_restored,fs_original,pm_restored,pm_original  ) )

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
        pm.port_close()
        
        logging.debug( "Finished SMELLIE PQ laser intensity scan (default NI trigger). pass: {}/{}, fail:{}/{}".format(npass,npass+nfail,nfail,npass+nfail) )
        
    except Exception, e:
        logging.debug( "Exception:" )
        logging.debug( e )

