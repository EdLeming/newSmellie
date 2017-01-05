# Test the SMELLIE SuperK laser
# functions to test the functionality of the SuperK control code
# Test with the spectrometer (or, alternatively the power meter)

import logging, time, datetime
from smellie import superk_driver
from smellie import fibre_switch
from smellie import power_meter
from superk import SuperK
#import matplotlib.pyplot as plt
import numpy

pm = power_meter.PowerMeter()
fs = fibre_switch.FibreSwitch()
sk = superk_driver.SuperK()

logging.basicConfig(filename=r'C:\SMELLIE\logs\test_superk_spectrum.log', filemode="a", level=logging.DEBUG)
console = logging.StreamHandler() #print logger to console
console.setLevel(logging.DEBUG)
logging.getLogger('').addHandler(console)

npass = 0
nfail = 0

try:
    logging.debug( "Begin Testing SMELLIE SuperK spectrum. {}".format( datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') ) )   
    
    fs.set_global_channel_number(70)
    
    pm.port_open()
    sk.port_open()
    
    COMPort = "COM4"
    controlBits = SuperK.getSuperKControls(COMPort)
    controlBits.trigMode = 0
    controlBits.internalPulseFreqHz = 20000
    SuperK.setSuperKControls(COMPort,controlBits)

    wavelengths = range(405,755,2)
    powerDataMean = []
    powerRangeDataMean = []
    powerDataSD = []
    variaBW = 10
    npulses = 1000
    
    sk.go_ready(0,(wavelengths[0]-variaBW/2)*10,(wavelengths[0]+variaBW/2)*10)
    
    for setWavelength in wavelengths:
    
        #iterate power meter wavelength calibration
        pm.set_wavelength(setWavelength)
        readWavelength = pm.get_wavelength()
        if (readWavelength!=setWavelength): 
            raise Exception("nope")
            break
        
        sk.go_ready(0,(setWavelength-variaBW/2)*10,(setWavelength+variaBW/2)*10)
        
        time.sleep(0.5)
        
        #get power measurement from power meter
        
        powerData = numpy.array([])
        powerRangeData = numpy.array([])
        for x in range(11):
            power = pm.get_power()
            powerRange = pm.get_power_range()
            powerData = numpy.append(powerData,power)
            powerRangeData = numpy.append(powerRangeData,powerRange)
            time.sleep(0.1)
        
        powermean = numpy.mean(powerData)
        powersd = numpy.std(powerData)
        powerrange = numpy.amax(powerRangeData)
        
        powerDataMean.append( powermean )
        powerDataSD.append( powersd )
        powerRangeDataMean.append( powerrange )

        print "(Wavelength, Power, SD, Range): {}, {}, {}, {}".format(setWavelength, powermean, powersd, powerrange)
        
    sk.go_safe()
    sk.port_close()
    pm.port_close()
    
    fileOut = open(r'C:\SMELLIE\workDiary\test_superk_spectrum.dat', 'a')
    fileOut.write('Wavelength(nm),MeanIntensity(W),SDIntensity(W),MeterRange(W)\n')
    for i,j,k,l in zip(wavelengths,powerDataMean,powerDataSD,powerRangeDataMean):
        fileOut.write( '{},{},{},{}\n'.format( i,j,k,l ) )
    fileOut.closed
    
    logging.debug( "Finished Testing SMELLIE SuperK spectrum" )
    
    #plt.errorbar(wavelengths,powerDataMean, yerr=powerDataSD,fmt='o')
    #plt.axis([400,750,1E-10,3E-9])
    #plt.show()
    
except Exception, e:
    logging.debug( "Exception: {}".format(e) )