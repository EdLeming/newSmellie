# Test the SMELLIE SuperK laser
# functions to test the functionality of the SuperK control code
# Test with the spectrometer (or, alternatively the power meter)

import logging, time, datetime, numpy
from multiprocessing.pool import ThreadPool
from smellie import superk_driver, ni_analog_read, ni_trigger_generator, superk
import matplotlib.pyplot as plt

def measure_voltage(number_of_samples, sampling_frequency):
    voltage,sd = ar.read_voltage_mean(number_of_samples, sampling_frequency)
    return voltage,sd

sk = superk_driver.SuperkDriver()
ar = ni_analog_read.AnalogRead()
tg = ni_trigger_generator.TriggerGenerator()
pool = ThreadPool(processes=1)

logging.basicConfig(filename=r'C:\SMELLIE\logs\test_superk_pulse_distribution.log', filemode="w", level=logging.DEBUG)
console = logging.StreamHandler() #print logger to console
console.setLevel(logging.DEBUG)
logging.getLogger('').addHandler(console)

try:
    logging.debug( "Begin Testing SMELLIE pulse distribution. {}".format( datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') ) )   
    
    sk.port_open()
    sk.go_safe()
    
    COMPort = "COM4"
    controlBits = superk.getSuperKControls(COMPort)
    controlBits.trigMode = 2
    controlBits.internalPulseFreqHz = 1000
    controlBits.burstPulses = 1000
    superk.setSuperKControls(COMPort,controlBits)

    wavelength = 4950
    bandwidth = 100
    intensity = 0
    number_of_triggers = 1
    trigger_frequency = 1
    number_of_samples = 100000
    sampling_frequency = 100000

    sk.go_ready(intensity,wavelength-bandwidth/2,wavelength+bandwidth/2)
    
    measure_parameters = (number_of_samples, sampling_frequency)
    #async_measure_voltage = pool.apply_async(measure_voltage, measure_parameters)
    
    tg.generate_triggers(number_of_triggers, trigger_frequency, 'SUPERK')
    #voltages = async_measure_voltage.get()
    voltages = numpy.zeros()

    fileOut = open(r'C:\SMELLIE\workDiary\test_superk_pulse_distribution.dat'.format(wavelength), 'w')
    fileOut.write('MPU_Voltage_sample, wavelength: {}, pulses: {}, rate: {}, intensity: {}\n'.format(wavelength, number_of_triggers, trigger_frequency, intensity) )
    for i in range(number_of_samples):
        fileOut.write( '{}\n'.format( voltages[i] ) )
    fileOut.closed
    
    #sk.go_safe()
    sk.port_close()
     
    logging.debug( "Finished Testing SMELLIE pulse distribution. {}".format( datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') ) )
    
    plt.plot(voltages)
    plt.axis([0,number_of_samples,0,3])
    plt.show()
    
except Exception, e:
    logging.debug( "Exception: {}".format(e) )