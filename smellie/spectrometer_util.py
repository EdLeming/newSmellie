from time import sleep
from ctypes import OleDLL, create_string_buffer, c_double, c_int16, c_int32, byref
from smellie_config import SPEC_DLL_PATH, SPEC_STR_BUFFER_SIZE
from functools import wraps
import os

"""
Core functions for use in the Ocean Optics Spectrometer package - not intended for use outside.
"""

def string_buffer():
    """   
    :returns: ctype string buffer, the size of which is set in :mod:config
    """
    return create_string_buffer(SPEC_STR_BUFFER_SIZE)
    
class SpecDLLError(Exception):
    """
    Raised if an exception is flagged up *during* a call to the .dll
    """
    pass

class SpecLogicError(Exception):
    """
    Raised *before* any call to the .dll if function arguments are incorrect
    """
    pass

# Open the .dll on import
if not os.path.exists(SPEC_DLL_PATH):
    raise SpecLogicError("Cannot open dll on path {0}".format(SPEC_DLL_PATH))
try:
    dll = OleDLL(SPEC_DLL_PATH)
except Exception as e:
    raise SpecLogicError("Opening dll failed! : {0}".format(str(e))) 

# Error Handling and Decoding
def decode_error(COMPort, iErr):
    """
    Decodes an error code thrown by the hardware. 
    If the translation fails, this returns: unknown error code.

    :param iErr: .dll generated error code

    :returns: error message
    :type error message: string
    """
    str_buff = create_string_buffer(SPEC_STR_BUFFER_SIZE)
    try:
        #dll.OOUtil_DecodeError(COMPort, c_int32(iErr), str_buff, c_int32(SPEC_STR_BUFFER_SIZE) )
        return str_buff.value
    except WindowsError:
        return "Spec Library: unknown error code {0}".format(iErr)

def raise_on_error_code(in_function):
    """
    OleDll automatically detects a non-zero exit code and throws a WindowsException.
    This decorator produces a modified function that catches this, extracts and translates the error code, and throws a SepiaDLLError.

    :param in_function: the function to wrap

    :returns: a logically equivalent function that catches WindowsError exceptions thrown by ctypes, extracts and decodes the error code then re-throws as SepiaDLLError
    """
    @wraps(in_function)
    def modified(*args, **kwargs):
        try:
            return in_function(*args, **kwargs)
        except WindowsError as e:
            raise SpecDLLError(decode_error(e.winerror))
    return modified
    
#def createWrapper(runnumber): 
#    #set up logging
#    logging.basicConfig(filename='c:\SMELLIE\logs\OOspectrometerLogRun{}.log'.format(runnumber), filemode="w", level=logging.DEBUG)
#    console = logging.StreamHandler() #print logger to console
#    console.setLevel(logging.INFO)
#    logging.getLogger('').addHandler(console)
    
def initialise():
    """   
    :undocumented
    """
    wrapper = createWrapper()
    openAllSpectrometers(wrapper)
    getName(wrapper)
    getFirmwareVersion(wrapper)
    getSerialNumber(wrapper)
    
    #set acquisition parameters
    setExternalTriggerMode(wrapper,0)
    setBoxcarWidth(wrapper, 0)
    setCorrectForDetectorNonlinearity(wrapper,1)
    setCorrectForElectricalDark(wrapper,1)
    setIntegrationTime(wrapper,10000)
    setScansToAverage(wrapper,1)
    
    #set external trigger delay
    extTrigDelay = getFeatureControllerExternalTriggerDelay(wrapper)
    setExternalTriggerDelay(extTrigDelay,1000)

def shutdown(wrapper):
    """   
    :undocumented
    """
    destroyExternalTriggerDelay()
    closeAllSpectrometers(wrapper)    
    destroyWrapper(wrapper)
    
    
@raise_on_error_code
def createWrapper():
    """   
    :undocumented
    """
    #uint64_t __cdecl Wrapper_Create(void);
    wrapper = dll.OOUtil_Wrapper_Create()
    #logging.info( 'Create Wrapper: {}'.format(wrapper) )
    return wrapper

def destroyWrapper(wrapper):
    """   
    :undocumented
    """
    #void __cdecl Wrapper_Destroy(uint64_t Wrapper);
    #wrapperIn = c_uint64(wrapper)
    dll.OOUtil_Wrapper_Destroy(wrapper)
    #logging.info( 'Destroy Wrapper: {}'.format(wrapper.value) )

def openAllSpectrometers(wrapper):
    """   
    :undocumented
    """
    #void __cdecl Wrapper_openAllSpectrometers(uint64_t WrapperIn, int32_t *NumberOfSpectrometers);
    #wrapperIn = c_uint64(wrapper)
    numberOfSpectrometers = c_int32(-1)
    dll.OOUtil_Wrapper_openAllSpectrometers(wrapper, byref(numberOfSpectrometers) )
    #logging.info( 'Open All Spectrometers: {}, number of spectrometers: {}'.format(wrapper.value, numberOfSpectrometers.value) )
    return numberOfSpectrometers

def closeAllSpectrometers(wrapper):
    """   
    :undocumented
    """
    #void __cdecl Wrapper_closeAllSpectrometers(uint64_t WrapperIn);
    #wrapperIn = c_uint64(wrapper)
    dll.OOUtil_Wrapper_closeAllSpectrometers(wrapper)
    #logging.info( 'Close All Spectrometers: {}'.format(wrapper.value) )

def getFirmwareVersion(wrapper):
    """   
    :undocumented
    """
    #void __cdecl Wrapper_getFirmwareVersion(uint64_t Wrapper, int32_t Index, char Firmware[], int32_t len);
    #wrapperIn = c_uint64(wrapper)
    index = c_int32(0)
    message = string_buffer()
    dll.OOUtil_Wrapper_getFirmwareVersion(wrapper, index, message, c_int32(SPEC_STR_BUFFER_SIZE) )
    #logging.info( 'get Firmware Version: {}'.format(message) )
    return message.value

def getName(wrapper):
    """   
    :undocumented
    """
    #void __cdecl Wrapper_getName(int32_t Index, uint64_t Wrapper, char SpectrometerName[], int32_t len);
    #wrapperIn = c_uint64(wrapper)
    index = c_int32(0)
    message = string_buffer()
    dll.OOUtil_Wrapper_getName(index, wrapper, message, c_int32(SPEC_STR_BUFFER_SIZE) )
    #logging.info( 'Spectrometer Name: {}'.format(message) )
    return message.value

def getSerialNumber(wrapper):
    """   
    :undocumented
    """
    #void __cdecl Wrapper_getSerialNumber(uint64_t Wrapper, int32_t Index, char SerialNumber[], int32_t len);
    #wrapperIn = c_uint64(wrapper)
    index = c_int32(0)
    message = string_buffer()
    dll.OOUtil_Wrapper_getSerialNumber( wrapper, index, message, c_int32(SPEC_STR_BUFFER_SIZE) )
    #logging.info( 'Serial Number: {}'.format(message) )
    return message.value

def getIntegrationTime(wrapper):
    """   
    :undocumented
    """
    #int32_t __cdecl Wrapper_getIntegrationTime(uint64_t Wrapper, int32_t Index);
    #wrapperIn = c_uint64(wrapper)
    index = c_int32(0)
    retValue = dll.OOUtil_Wrapper_getIntegrationTime(wrapper, index)
    #logging.info( 'Get Integration Time: {}'.format(retValue.value) )
    return retValue.value

def setIntegrationTime(wrapper,value):
    """   
    :undocumented
    """
    #void __cdecl Wrapper_setIntegrationTime(uint64_t WrapperIn, int32_t Index, int32_t IntegrationTime);
    #wrapperIn = c_uint64(wrapper)
    index = c_int32(0)
    integrationTime = c_int32(value)
    minIntegrationTime = getMinimumIntegrationTime(wrapper)
    maxIntegrationTime = getMaximumIntegrationTime(wrapper)
    
    if (value>=minIntegrationTime or value<=maxIntegrationTime):
        dll.OOUtil_Wrapper_setIntegrationTime(wrapper, index, integrationTime)
        #int32_t __cdecl Wrapper_getIntegrationTime(uint64_t Wrapper, int32_t Index);
        retValue = dll.OOUtil_Wrapper_getIntegrationTime(wrapper, index)
        #logging.info( 'Set Integration Time: {}'.format(retValue.value) )
        if (retValue.value!=integrationTime.value):
            raise SpecDLLError( 'Unable to Set Integration Time. Tried: {}, Current: {}'.format(integrationTime.value,retValue.value) )
    else:
        raise SpecLogicError( 'Unable to Set Integration Time. Tried: {}. Must be greater than {} and less than {}.'.format(integrationTime.value,minIntegrationTime,maxIntegrationTime) )

def getScansToAverage(wrapper):
    """   
    :undocumented
    """
    #int32_t __cdecl Wrapper_getScansToAverage(uint64_t Wrapper, int32_t Index);
    #wrapperIn = c_uint64(wrapper)
    index = c_int32(0)
    retValue = dll.OOUtil_Wrapper_getScansToAverage(wrapper, index)
    #logging.info( 'Get Scans to average: {}'.format(retValue.value) )
    return retValue.value

def setScansToAverage(wrapper,value):
    """   
    :undocumented
    """
    #void __cdecl Wrapper_setScansToAverage(uint64_t WrapperIn, int32_t Index, int32_t Average);
    #wrapperIn = c_uint64(wrapper)
    index = c_int32(0)
    average = c_int32(value)
    dll.OOUtil_Wrapper_setScansToAverage(wrapper, index, average)
    
    #int32_t __cdecl Wrapper_getScansToAverage(uint64_t Wrapper, int32_t Index);
    retValue = dll.OOUtil_Wrapper_getScansToAverage(wrapper, index)
    #logging.info( 'Set Scans to average: {}'.format(retValue.value) )
    if (retValue.value!=average.value):
        raise SpecDLLError( 'Unable to Set Scans to Average. Tried: {}, Current: {}'.format(average.value,retValue.value) )

def getSpectrum(wrapper):
    """   
    :undocumented
    """
    #void __cdecl Wrapper_getSpectrum  (uint64_t Wrapper, int32_t Index, double SpectrumValues[], int32_t *Length, int32_t len);
    #wrapperIn = c_uint64(wrapper)
    index = c_int32(0)
    length = int(getNumberOfPixels(wrapper))
    spectrumLength = c_int32(-1)
    spectrumValues = (c_double*length)()
    dll.OOUtil_Wrapper_getSpectrum(wrapper, index, byref(spectrumValues), byref(spectrumLength), c_int32(length) )
    l#ogging.info( 'Get Spectrum, SpectrumLength: {}'.format(spectrumLength.value) )
    return list(spectrumValues)

def getWavelengths(wrapper):
    """   
    :undocumented
    """
    #void __cdecl Wrapper_getWavelengths(uint64_t Wrapper, int32_t Index, double WLValues[], int32_t *Length, int32_t len);
    #wrapperIn = c_uint64(wrapper)
    index = c_int32(0)
    length = int(getNumberOfPixels(wrapper))
    wavelengthLength = c_int32(-1)
    wavelengthValues = (c_double*length)()

    dll.OOUtil_Wrapper_getWavelengths(wrapper, index, byref(wavelengthValues), byref(wavelengthLength), c_int32(length) )
    #print "Get Wavelengths:"
    #print list(wavelengthValues)
    #logging.info( 'Get Wavelengths, WavelengthLength: {}'.format(wavelengthLength.value) )
    return list(wavelengthValues)

def writeSpectrum(runNumber,wavelengthData,spectrumData):
    """   
    :undocumented
    """
    fileOut = open('C:\SMELLIE\data\spec\OOspectrometerDataRun{}.csv'.format(runNumber), 'a')
    fileOut.write( 'Wavelength(nm),Intensity(arb)\n')
    for i,j in zip(wavelengthData,spectrumData):
        fileOut.write( '{},{}\n'.format( i,j ) )
    fileOut.closed

def getFeatureControllerIrradianceCalibrationFactor(wrapper):
    """   
    :undocumented
    """
    #uint64_t __cdecl Wrapper_getFeatureControllerIrradianceCalibrationFactor(uint64_t Wrapper, int32_t index);
    #wrapperIn = c_uint64(wrapper)
    index = c_int32(0)
    retValue = dll.OOUtil_Wrapper_getFeatureControllerIrradianceCalibrationFactor(wrapper, index)
    #logging.info( 'Get FeatureControllerIrradianceCalibrationFactor: {}'.format(retValue.value) )
    return retValue.value

def getFeatureControllerExternalTriggerDelay(wrapper):
    """   
    :undocumented
    """
    #uint64_t __cdecl Wrapper_getFeatureControllerExternalTriggerDelay(uint64_t Wrapper, int32_t Index);
    #wrapperIn = c_uint64(wrapper)
    index = c_int32(0)
    retValue = dll.OOUtil_Wrapper_getFeatureControllerExternalTriggerDelay(wrapper, index)
    #logging.info( 'Get FeatureControllerExternalTriggerDelay: {}'.format(retValue.value) )
    return retValue.value

def getExternalTriggerMode(wrapper):
    """   
    :undocumented
    """
    #int32_t __cdecl Wrapper_getExternalTriggerMode(uint64_t Wrapper, int32_t Index);
    #wrapperIn = c_uint64(wrapper)
    index = c_int32(0)
    retValue = dll.OOUtil_Wrapper_getExternalTriggerMode(wrapper, index)
    #logging.info( 'Get External Trigger Mode: {}'.format(retValue.value) )
    return retValue.value

def setExternalTriggerMode(wrapper,value):
    """   
    :undocumented
    """
    #void __cdecl Wrapper_setExternalTriggerMode(uint64_t WrapperIn, int32_t Index, int32_t TriggerMode);
    #wrapperIn = c_uint64(wrapper)
    index = c_int32(0)
    triggerMode = c_int32(value)
    dll.OOUtil_Wrapper_setExternalTriggerMode(wrapper, index, triggerMode)

    #int32_t __cdecl Wrapper_getExternalTriggerMode(uint64_t Wrapper, int32_t Index);
    retValue = dll.OOUtil_Wrapper_getExternalTriggerMode(wrapper, index)
    #logging.info( 'Set External Trigger Mode: {}'.format(retValue.value) )
    if (retValue.value!=triggerMode.value):
        raise SpecDLLError( 'Unable to Set External Trigger Mode. Tried: {}, Current: {}'.format(triggerMode.value,retValue.value) )

def setCorrectForElectricalDark(wrapper,value):
    """   
    :undocumented
    """
    #void __cdecl Wrapper_setCorrectForElectricalDark(uint64_t WrapperIn, int32_t Index, int32_t OnOff);
    wrapperIn = c_uint64(wrapper)
    index = c_int32(0)
    flag = c_int32(value)
    if (flag.value==0 or flag.value==1):
        dll.OOUtil_Wrapper_setCorrectForElectricalDark(wrapper, index, flag)
        #logging.info( 'Set Correct For Electrical Dark: {}'.format(flag.value) )
    else:
        raise SpecLogicError( 'Unable to Set Correct For Electrical Dark. Tried: {}. Note: must be 0 or 1.'.format(flag.value) )

def setCorrectForDetectorNonlinearity(wrapper,value):
    """   
    :undocumented
    """
    #void __cdecl Wrapper_setCorrectForDetectorNonlinearity(uint64_t WrapperIn, int32_t Index, int32_t OnOff);
    #wrapperIn = c_uint64(wrapper)
    index = c_int32(0)
    flag = c_int32(value)
    if (flag.value==0 or flag.value==1):
        dll.OOUtil_Wrapper_setCorrectForDetectorNonlinearity(wrapper, index, flag)
        #logging.info( 'Set Correct For Detector Nonlinearity: {}'.format(flag.value) )
    else:
        raise SpecLogicError( 'Unable to Set Correct For Detector Nonlinearity. Tried: {}. Note: must be 0 or 1.'.format(flag.value) )

def getBoxcarWidth(wrapper):
    """   
    :undocumented
    """
    #int32_t __cdecl Wrapper_getBoxcarWidth(uint64_t Wrapper, int32_t Index);
    #wrapperIn = c_uint64(wrapper)
    index = c_int32(0)
    boxcarWidth = dll.OOUtil_Wrapper_getBoxcarWidth(wrapper, index)
    #logging.info( 'Get Boxcar Width: {}'.format(boxcarWidth.value) )
    return retValue.value

def setBoxcarWidth(wrapper,value):
    """   
    :undocumented
    """
    #void __cdecl Wrapper_setBoxcarWidth(uint64_t WrapperIn, int32_t Index, int32_t BoxcarWidth);
    #wrapperIn = c_uint64(wrapper)
    index = c_int32(0)
    boxcarWidth = c_int32(value)
    dll.OOUtil_Wrapper_setBoxcarWidth(wrapper, index, boxcarWidth)

    #int32_t __cdecl Wrapper_getBoxcarWidth(uint64_t Wrapper, int32_t Index);
    retValue = dll.OOUtil_Wrapper_getBoxcarWidth(wrapper, index)
    #logging.info( 'Set Boxcar Width: {}'.format(retValue.value) )
    if (retValue.value!=boxcarWidth.value):
        raise SpecDLLError( 'Unable to Set Boxcar Width. Tried: {}, Current: {}'.format(boxcarWidth.value,retValue.value) )

def getMaximumIntensity(wrapper):
    """   
    :undocumented
    """
    #int32_t __cdecl Wrapper_getMaximumIntensity(uint64_t Wrapper, int32_t Index);
    #wrapperIn = c_uint64(wrapper)
    index = c_int32(0)
    retValue = dll.OOUtil_Wrapper_getMaximumIntensity(wrapper, index)
    #logging.info( 'Get Maximum Intensity: {}'.format(retValue.value) )
    return retValue.value

def getMaximumIntegrationTime(wrapper):
    """   
    :undocumented
    """
    #int32_t __cdecl Wrapper_getMaximumIntegrationTime(uint64_t Wrapper, int32_t Index);
    #wrapperIn = c_uint64(wrapper)
    index = c_int32(0)
    retValue = dll.OOUtil_Wrapper_getMaximumIntegrationTime(wrapper, index)
    #logging.info( 'Get Maximum Integration Time: {}'.format(retValue.value) )
    return retValue.value

def getMinimumIntegrationTime(wrapper):
    """   
    :undocumented
    """
    #int32_t __cdecl Wrapper_getMinimumIntegrationTime(uint64_t Wrapper, int32_t Index);
    #wrapperIn = c_uint64(wrapper)
    index = c_int32(0)
    retValue = dll.OOUtil_Wrapper_getMinimumIntegrationTime(wrapper, index)
    #logging.info( 'Get Minimum Integration Time: {}'.format(retValue.value) )
    return retValue.value

def getNumberOfDarkPixels(wrapper):
    """   
    :undocumented
    """
    #int32_t __cdecl Wrapper_getNumberOfDarkPixels(uint64_t Wrapper, int32_t Index);
    #wrapperIn = c_uint64(wrapper)
    index = c_int32(0)
    retValue = dll.OOUtil_Wrapper_getNumberOfDarkPixels(wrapper, index)
    #logging.info( 'Get Number Of Dark Pixels: {}'.format(retValue.value) )
    return retValue.value

def getNumberOfPixels(wrapper):
    """   
    :undocumented
    """
    #int32_t __cdecl Wrapper_getNumberOfPixels(uint64_t Wrapper, int32_t Index);
    #wrapperIn = c_uint64(wrapper)
    index = c_int32(0)
    retValue = dll.OOUtil_Wrapper_getNumberOfPixels(wrapper, index)
    #logging.info( 'Get Number Of Pixels: {}'.format(retValue.value) )
    return retValue.value

def isSaturated(wrapper):
    """   
    :undocumented
    """
    #uint8_t __cdecl Wrapper_isSaturated(uint64_t Wrapper, int32_t Index);
    #wrapperIn = c_uint64(wrapper)
    index = c_int32(0)
    retValue = dll.OOUtil_Wrapper_isSaturated(wrapper, index)
    #logging.info( 'is Saturated?: {}'.format(retValue.value) )
    return retValue.value

def getLastException(wrapper):
    """   
    :undocumented
    """
    #void __cdecl Wrapper_getLastException(uint64_t Wrapper, char LastException[], int32_t len);
    #wrapperIn = c_uint64(wrapper)
    message = string_buffer()
    dll.OOUtil_Wrapper_getLastException(wrapper, message, c_int32(SPEC_STR_BUFFER_SIZE) )
    #logging.info( 'Get Last Exception: {}'.format(message) )
    return message.value

def destroyExternalTriggerDelay():
    """   
    :undocumented
    """
    #void __cdecl ExternalTriggerDelay_Destroy(void);
    dll.OOUtil_ExternalTriggerDelay_Destroy()
    #logging.info( 'Destroy external Trigger Delay.' )

def getExternalTriggerDelayMaximum(externalTriggerDelay):
    """   
    :undocumented
    """
    #int32_t __cdecl ExternalTriggerDelay_getExternalTriggerDelayMaximum(uint64_t ExternalTriggerDelay);
    externalTriggerDelayIn = c_uint64(externalTriggerDelay)
    retValue = dll.OOUtil_ExternalTriggerDelay_getExternalTriggerDelayMaximum(externalTriggerDelayIn)
    #logging.info( 'Get External Trigger Delay Maximum: {}'.format(retValue.value) )
    return retValue.value

def getExternalTriggerDelayMinimum(externalTriggerDelay):
    """   
    :undocumented
    """
    #int32_t __cdecl ExternalTriggerDelay_getExternalTriggerDelayMinimum(uint32_t ExternalTriggerDelay);
    externalTriggerDelayIn = c_uint64(externalTriggerDelay)
    retValue = dll.OOUtil_ExternalTriggerDelay_getExternalTriggerDelayMinimum(externalTriggerDelayIn)
    #logging.info( 'Get External Trigger Delay Minimum: {}'.format(retValue.value) )
    return retValue.value

def setExternalTriggerDelay(externalTriggerDelay,value):
    """   
    :undocumented
    """
    #void __cdecl ExternalTriggerDelay_setExternalTriggerDelay(uint64_t ExternalTriggerDelayIn, int32_t microseconds);
    externalTriggerDelayIn = c_uint64(externalTriggerDelay)
    delayTime = c_int32(value)
    minTime = getExternalTriggerDelayMinimum(externalTriggerDelay)
    maxTime = getExternalTriggerDelayMaximum(externalTriggerDelay)
    if (value>=minTime or value<=maxTime):
        dll.OOUtil_ExternalTriggerDelay_setExternalTriggerDelay(externalTriggerDelayIn, delayTime)
        #logging.info( 'Set External Trigger Delay: {}'.format(delayTime.value) )
    else:
        raise SpecLogicError( 'Unable to Set External Trigger Delay. Tried: {}. Must be greater than {} and less than {}.'.format(delayTime.value,minTime,maxTime) )
