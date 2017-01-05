# Calibrate the gain setting for the SuperK laser for each wavelength
# Runs scan of each wavelength while incrementing the gain voltage.

import logging, time, datetime, numpy
from multiprocessing.pool import ThreadPool
from smellie import superk_driver, ni_trigger_generator, ni_analog_read, ni_gain_control

def measure_voltage():
    voltage,sd = ar.read_voltage()
    return voltage,sd

if __name__ == "__main__":

    logging.basicConfig(filename=r'C:\SMELLIE\logs\test_superk_gain_cal.log', filemode="a", level=logging.DEBUG)
    console = logging.StreamHandler() #print logger to console
    console.setLevel(logging.DEBUG)
    logging.getLogger('').addHandler(console)

    try:
        sk = superk_driver.SuperkDriver()
        tg = ni_trigger_generator.TriggerGenerator()
        ar = ni_analog_read.AnalogRead()
        gc = ni_gain_control.GainVoltageGenerator()
        pool = ThreadPool(processes=1)

        logging.debug( "Begin SMELLIE superk gain calibration. {}".format( datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') ) )

        #open devices
        sk.port_open()
        sk.go_safe()

        wavelengths = range(4050,7551,50) #test wavelengths 405 thru 755 in 5nm steps

        trig_npulses = 50
        trig_rate = 10
        bandwidth = 100
        intensity = 1
        
        gain_offset = 0.0044 # GAIN_CONTROL_VOLTAGE_OFFSET in config file

        for wavelength in wavelengths:
        
            logging.debug( "Begin calibration of superk laser. Central wavelength: {}".format(wavelength) )
            gains = range(0,1000,10) #from 0 to 1V in small steps
            voltages = []
            sds = []
            
            sk.go_safe()
            wavelength_low = wavelength-bandwidth/2
            wavelength_high = wavelength+bandwidth/2
            sk.go_ready(intensity,wavelength_low, wavelength_high)
            
            for gain in gains:
                gc.generate_voltage(float(gain)/1000.+gain_offset)
                time.sleep(0.5)
                async_measure_voltage = pool.apply_async(measure_voltage)
                logging.debug('Triggers. pulses = {}, rate = {}'.format(trig_npulses, trig_rate))
                tg.generate_triggers(trig_npulses, trig_rate, 'SUPERK')
                voltage, sd = async_measure_voltage.get()
                voltages.append( voltage )
                sds.append( sd )

                logging.debug ( "(wavelength, gain(V), MPU_Mean_Voltage(V), SD(V)): {}, {}, {}, {}\n".format(wavelength, float(gain)/1000.+gain_offset, voltage, sd) )
     
            fileOut = open(r'C:\SMELLIE\workDiary\test_gain_cal_superk_{}nm.dat'.format(wavelength), 'a')
            fileOut.write('wavelength: {}&{}, Repetition Rate: {}, Npulses: {}, Bandwidth: {}, Intensity: {}, Gain offset: {}\n'.format(wavelength_low, wavelength_high, trig_rate, trig_npulses, bandwidth, intensity, gain_offset))
            fileOut.write('Gain(V), MPU_Mean_Voltage(V), SD(V)\n')
            for i,j,k in zip(gains,voltages,sds):
                fileOut.write( '{},{},{}\n'.format( float(i)/1000.+gain_offset,j,k ) )
            fileOut.closed

        #go back to safe, original states
        gc.generate_voltage(0+gain_offset)
        sk.go_safe()
        sk.port_close() #close laser
        logging.debug( "Current settings." )

        logging.debug( "Finished SMELLIE SUPERK gain calibration." )

    except Exception, e:
        logging.debug( "Exception:" )
        logging.debug( e )

