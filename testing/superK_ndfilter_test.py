# Test the SMELLIE SuperK laser
# functions to test the functionality of the SuperK control code
# Test with the spectrometer (or, alternatively the power meter)

import logging, time, datetime, numpy
from smellie import superk_driver, fibre_switch, power_meter, SuperK
#import matplotlib.pyplot as plt

pm = power_meter.PowerMeter()
fs = fibre_switch.FibreSwitch()
sk = superk_driver.SuperK()

logging.basicConfig(filename=r'C:\SMELLIE\logs\test_superk_ndfilter.log', filemode="a", level=logging.DEBUG)
console = logging.StreamHandler() #print logger to console
console.setLevel(logging.DEBUG)
logging.getLogger('').addHandler(console)

npass = 0
nfail = 0

try:
    logging.debug( "Begin Testing SMELLIE ND filter. {}".format( datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') ) )   
    
    fs.set_global_channel_number(70)
    
    pm.port_open()
    sk.port_open()
    
    COMPort = "COM4"
    controlBits = SuperK.getSuperKControls(COMPort)
    controlBits.trigMode = 0
    controlBits.internalPulseFreqHz = 20000
    SuperK.setSuperKControls(COMPort,controlBits)

    wavelengths = range(405,721,10)
    variaBW = 10
    
    NDPositions = range(250,501,1)
    
    sk.go_ready(0,(wavelengths[0]-variaBW/2)*10,(wavelengths[0]+variaBW/2)*10)
    
    for setWavelength in wavelengths:
        powerDataMean = []
        powerRangeDataMean = []
        powerDataSD = []
        sk.go_ready(0,(setWavelength-variaBW/2)*10,(setWavelength+variaBW/2)*10)
        pm.set_wavelength(setWavelength)
        print sk.NDfilter_position()
        sk.NDfilter_set_position(-1*250)
        time.sleep(60)
        print sk.NDfilter_position()
        time.sleep(1)
    
        for currentNDPosition in NDPositions:

            sk.NDfilter_set_position(-1*currentNDPosition)
            
            time.sleep(0.1)
            
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

            print "(Wavelength, NDPosition, Power, SD, Range): {}, {}, {}, {}, {}".format(setWavelength, currentNDPosition, powermean, powersd, powerrange)

        fileOut = open(r'C:\SMELLIE\workDiary\test_superk_ndfilter_{}nm.dat'.format(setWavelength), 'a')
        fileOut.write('NDposition,MeanIntensity(W),SDIntensity(W),MeterRange(W)\n')
        for i,j,k,l in zip(NDPositions,powerDataMean,powerDataSD,powerRangeDataMean):
            fileOut.write( '{},{},{},{}\n'.format( i,j,k,l ) )
        fileOut.closed
    
    print sk.NDfilter_position()
    sk.NDfilter_set_position(-1*1)
    time.sleep(200)
    print sk.NDfilter_position()
    
    sk.go_safe()
    sk.port_close()
    pm.port_close()
    
    logging.debug( "Finished Testing SMELLIE SuperK ND filter" )
    
    #plt.errorbar(NDPositions,powerDataMean, yerr=powerDataSD,fmt='o')
    #plt.axis([000,450,1E-10,1E-6])
    #plt.show()
    
except Exception, e:
    logging.debug( "Exception: {}".format(e) )