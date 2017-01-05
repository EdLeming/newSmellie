# Calibrate the gain setting for each PQ laser
# Runs scan of each laser while incrementing the gain voltage (also uses laser switch).

import logging, time, datetime, numpy
from multiprocessing.pool import ThreadPool
from smellie import laser_driver, laser_switch, ni_trigger_generator, ni_analog_read, ni_gain_control

def measure_voltage():
    voltage,sd = ar.read_voltage_mean()
    return voltage,sd

if __name__ == "__main__":

    logging.basicConfig(filename=r'C:\SMELLIE\logs\test_PQ_gain_cal.log', filemode="a", level=logging.DEBUG)
    console = logging.StreamHandler() #print logger to console
    console.setLevel(logging.DEBUG)
    logging.getLogger('').addHandler(console)

    try:
        ld = laser_driver.LaserDriver()
        ls = laser_switch.LaserSwitch()
        tg = ni_trigger_generator.TriggerGenerator()
        ar = ni_analog_read.AnalogRead()
        gc = ni_gain_control.GainVoltageGenerator()
        pool = ThreadPool(processes=1)
        
        logging.debug( "Begin SMELLIE PQ laser gain calibration. {}".format( datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') ) )
        
        #open devices
        ld.port_open()
        ld.go_safe()
     
        #record original settings
        ls_original = ls.get_active_channel()
        
        logging.debug( "Current settings: Laser switch chan: {}".format( ls_original ) )
        
        laser_numbers = range(1,5,1) #test lasers 1 thru 4

        trig_npulses = 50
        trig_rate = 10
        intensity = 1000
        
        gain_offset = 0.0044 # GAIN_CONTROL_VOLTAGE_OFFSET in config file

        for laser_number in laser_numbers:
        
            logging.debug( "Begin calibration of PQ laser: {}".format(laser_number) )
            gains = range(0,1000,10) #from 0 to 1V in small steps
            voltages = []
            sds = []
        
            ls_chan = ls.get_active_channel()
            #if (ls_chan != laser_number):
            ld.port_close() #close Sepia before laser switch d/c it.
            ls.set_active_channel(laser_number)
            ld.port_open()
            logging.debug( "Set: Laser switch chan: {}".format( ls.get_active_channel() ) )  
            #else:
            #    logging.debug( "Laser switch chan: {}".format( ls_chan ) )  
            
            ld.go_safe()
            ld.go_ready(intensity)
            
            for gain in gains:
                gc.generate_voltage(float(gain)/1000.+gain_offset)
                time.sleep(0.5)
                async_measure_voltage = pool.apply_async(measure_voltage)
                logging.debug('Triggers. pulses = {}, rate = {}'.format(trig_npulses, trig_rate))
                tg.generate_triggers(trig_npulses, trig_rate, 'PQ')
                voltage, sd = async_measure_voltage.get()
                voltages.append( voltage )
                sds.append( sd )

                logging.debug ( "(laser, gain(V), MPU_Mean_Voltage(V), SD(V)): {}, {}, {}, {}\n".format(laser_number, float(gain)/1000.+gain_offset, voltage, sd) )
     
            fileOut = open(r'C:\SMELLIE\workDiary\test_gain_cal_PQlaser{}.dat'.format(laser_number), 'a')
            fileOut.write('Laser: {}, Repetition Rate: {}, Npulses: {}, Laser intensity: {}, Gain offset: {}\n'.format(laser_number, trig_rate, trig_npulses, intensity, gain_offset))
            fileOut.write('Gain(V), MPU_Mean_Voltage(V), SD(V)\n')
            for i,j,k in zip(gains,voltages,sds):
                fileOut.write( '{},{},{}\n'.format( float(i)/1000.+gain_offset,j,k ) )
            fileOut.closed
     
        #go back to safe, original states
        gc.generate_voltage(0+gain_offset)
        ld.go_safe()
        ld.port_close() #close laser (before laser switch)
        ls.set_active_channel(ls_original)
        ls_restored = ls.get_active_channel()
        logging.debug( "Current settings (restored/original): Laser switch chan: {}/{}".format( ls_restored,ls_original ) )

        logging.debug( "Finished SMELLIE PQ laser gain calibration. ")
        
    except Exception, e:
        logging.debug( "Exception:" )
        logging.debug( e )

