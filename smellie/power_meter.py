from smellie_config import PM_ADDRESS
from time import sleep
from ctypes import OleDLL, create_string_buffer, c_int, c_double, c_uint, c_int16, c_int32, c_int64, byref
from smellie_config import PM_ADDRESS, PM_DLL_PATH, PM_STR_BUFFER_SIZE
from functools import wraps
import os
from smellie.smellie_logger import SMELLIELogger

class PowerMeterDLLError(Exception):
    """
    Raised if an exception is flagged up *during* a call to the .dll
    """
    pass

class PowerMeterLogicError(Exception):
    """
    Raised *before* any call to the .dll if function arguments are incorrect
    """
    pass

class PowerMeterHWError(Exception):
    """
    Thrown if an inconsistency is noticed *after* any hardware instruction is executed (i.e. a problem with the hardware itself)
    """
    pass

# Open the .dll on import
if not os.path.exists(PM_DLL_PATH):
    raise PowerMeterLogicError("Cannot open dll on path {0}".format(PM_DLL_PATH))
try:
    dll = OleDLL(PM_DLL_PATH)
except Exception as e:
    raise PowerMeterLogicError("Opening dll failed! : {0}".format(str(e)))
    
    
# Error Handling and Decoding
def decode_error(iErr):
    """
    Decodes an error code thrown by the hardware. 
    If the translation fails, this returns Power meter DLL: unknown error code.

    :param iErr: .dll generated error code

    :returns: error message
    :type error message: string
    """
    taskHandle = GetTaskHandle()
    str_buff = create_string_buffer(PM_STR_BUFFER_SIZE)
    try:
        dll.PM100DErrorMessage(byref(taskHandle), c_int32(iErr), None, str_buff, c_int32(PM_STR_BUFFER_SIZE) )
        return str_buff.value
    except WindowsError:
        return "PM Library: unknown error code {0}".format(iErr)

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
            raise PowerMeterDLLError(decode_error(e.winerror))
    return modified

@raise_on_error_code
def getTaskHandle():
    """   
    :undocumented
    """
    taskHandle = c_uint(0)
    dll.GetTaskHandle( PM_ADDRESS, byref(taskHandle) )
    if (taskHandle.value == 0):
        raise PowerMeterDLLError("Task handle not found.")
    return taskHandle

@raise_on_error_code
def getAttenuation(taskHandle, attributeSetValue):
    """   
    :undocumented
    """
    retValue = c_double()
    attributeSetValue = c_int16(attributeSetValue)
    dll.PM100DGetAttenuation(byref(taskHandle), attributeSetValue, None, byref(retValue))
    return retValue.value

@raise_on_error_code
def getDarkAdjustmentState(taskHandle):
    """   
    :undocumented
    """
    retValue = c_int16()
    dll.PM100DGetDarkAdjustmentState(byref(taskHandle), None, byref(retValue))
    return retValue.value

@raise_on_error_code
def getDarkOffset(taskHandle):
    """
    :undocumented
    """
    retValue = c_double()
    dll.PM100DGetDarkOffset(byref(taskHandle), None, byref(retValue))
    return retValue.value

@raise_on_error_code
def getPhotodiodeResponsivity(taskHandle, attributeSetValue):
    """
    :undocumented
    """
    retValue = c_double()
    attributeSetValue = c_int16(attributeSetValue)
    dll.PM100DGetPhotodiodeResponsivity(byref(taskHandle), attributeSetValue, None, byref(retValue))
    return retValue.value

@raise_on_error_code
def getThermopileResponsivity(taskHandle, attributeSetValue):
    """
    :undocumented
    """
    retValue = c_double()
    attributeSetValue = c_int16(attributeSetValue)
    dll.PM100DGetThermopileResponsivity(byref(taskHandle), attributeSetValue, None, byref(retValue))
    return retValue.value

@raise_on_error_code   
def getPyrosensorResponsivity(taskHandle, attributeSetValue):
    """
    :undocumented
    """
    retValue = c_double()
    attributeSetValue = c_int16(attributeSetValue)
    dll.PM100DGetPyrosensorResponsivity(byref(taskHandle), attributeSetValue, None, byref(retValue))
    return retValue.value

@raise_on_error_code
def getCalibrationMessage(taskHandle):
    """
    :undocumented
    """
    retValue = c_double()
    message = create_string_buffer(PM_STR_BUFFER_SIZE)
    dll.PM100DGetCalibrationMessage(byref(taskHandle), None, message, PM_STR_BUFFER_SIZE)
    return message.value

@raise_on_error_code
def getSensorInformation(taskHandle):
    """
    :undocumented
    """
    
    sensorFlags = c_int16()
    sensorSubtype = c_int16()
    sensorType = c_int16()
    sensorCalibrationMessage = create_string_buffer(PM_STR_BUFFER_SIZE)
    sensorName = create_string_buffer(PM_STR_BUFFER_SIZE)
    sensorSerialNumber = create_string_buffer(PM_STR_BUFFER_SIZE)
    
    dll.PM100DGetSensorInformation(byref(taskHandle), byref(sensorFlags), byref(sensorSubtype), byref(sensorType), sensorCalibrationMessage, None, sensorName, sensorSerialNumber, PM_STR_BUFFER_SIZE, PM_STR_BUFFER_SIZE, PM_STR_BUFFER_SIZE)
    return sensorFlags.value, sensorSubtype.value, sensorType.value, sensorCalibrationMessage.value, sensorName.value, sensorSerialNumber.value

@raise_on_error_code
def getPowerAutorangeMode(taskHandle):
    """
    :undocumented
    """
    retValue = c_int()
    dll.PM100DGetPowerAutorangeMode(byref(taskHandle), None, byref(retValue))
    return retValue.value

@raise_on_error_code
def getPowerReferenceState(taskHandle):
    """
    :undocumented
    """
    retValue = c_int()
    dll.PM100DGetPowerReferenceState(byref(taskHandle), None, byref(retValue))
    return retValue.value

@raise_on_error_code
def getPhotodiodeInputFilterState(taskHandle):
    """
    :undocumented
    """
    retValue = c_int()
    dll.PM100DGetPhotodiodeInputFilterState(byref(taskHandle), None, byref(retValue))
    return retValue.value
    
@raise_on_error_code
def getPowerReference(taskHandle, attributeSetValue):
    """
    :undocumented
    """
    retValue = c_double()
    attributeSetValue = c_int16(attributeSetValue)
    dll.PM100DGetPowerReference(byref(taskHandle), attributeSetValue, None, byref(retValue))
    return retValue.value

@raise_on_error_code
def getPowerUnit(taskHandle):
    """
    :undocumented
    """
    retValue = c_int16()
    dll.PM100DGetPowerUnit(byref(taskHandle), None, byref(retValue))
    return retValue.value

@raise_on_error_code
def setPowerUnit(taskHandle, setValue):
    """
    :undocumented
    """
    setValue = c_int16(setValue)
    dll.PM100DSetPowerUnit(byref(taskHandle), setValue, None)
    
@raise_on_error_code
def getDisplayContrast(taskHandle):
    """
    :undocumented
    """
    retValue = c_double()
    dll.PM100DGetDisplayContrast(byref(taskHandle), None, byref(retValue))
    return retValue.value

@raise_on_error_code
def setDisplayContrast(taskHandle, setValue):
    """
    :undocumented
    """
    setValue = c_double(setValue)
    dll.PM100DSetDisplayContrast(byref(taskHandle), setValue, None)
    
@raise_on_error_code
def getDisplayBrightness(taskHandle):
    """
    :undocumented
    """
    retValue = c_double()
    dll.PM100DGetDisplayBrightness(byref(taskHandle), None, byref(retValue))
    return retValue.value
    
@raise_on_error_code
def setDisplayBrightness(taskHandle, setValue):
    """
    :undocumented
    """
    setValue = c_double(setValue)
    dll.PM100DSetDisplayBrightness(byref(taskHandle), setValue, None)

@raise_on_error_code
def selfTest(taskHandle):
    """
    :undocumented
    """
    selfTestMessage = create_string_buffer(PM_STR_BUFFER_SIZE)
    selfTestResult = c_int16()
    dll.PM100DSelfTest(byref(taskHandle), None, selfTestResult, selfTestMessage, c_int32(PM_STR_BUFFER_SIZE) )
    return selfTestResult.value, selfTestMessage.value

class PowerMeter(object):

    def __init__(self):
        self.COMPort = PM_ADDRESS
        self.taskHandle = None
        self.attributeValue = 0
        self.isConnected = False

    @raise_on_error_code
    def port_open(self, iDQueryDoQuery=1, resetDevice=1):
        """   
        :returns: ctype string buffer, the size of which is set in :mod:config
        """
        SMELLIELogger.debug('SNODROP DEBUG: PowerMeter.port_open()')
        iDQueryDoQuery = c_int16(iDQueryDoQuery)
        resetDevice = c_int16(resetDevice)
        taskHandle = c_uint()
        dll.Initialise(self.COMPort, iDQueryDoQuery, resetDevice, byref(taskHandle) )
        self.taskHandle = taskHandle
        #run a quick self test
        selfTestResult, selfTestMessage = selfTest(self.taskHandle)
        if selfTestResult != 0:
            raise PowerMeterHWError("Self test of device failed. {}".format(message))
        #set default settings
        self.default_settings()
        self.isConnected = True

    @raise_on_error_code
    def port_close(self):
        """   
        :returns: ctype string buffer, the size of which is set in :mod:config
        """
        SMELLIELogger.debug('SNODROP DEBUG: PowerMeter.port_close()')
        if self.isConnected:
            dll.PM100DClose( byref(self.taskHandle) ) 
            self.isConnected = False
        else:
            raise PowerMeterLogicError("Power meter port not open.") 
        
        #to unload dll if it misbehaves.
        #handle = dll._handle 
        #windll.kernel32.FreeLibrary(handle)
        
    @raise_on_error_code
    def get_beam_diameter(self):
        """
        :undocumented
        """
        retValue = c_double()
        dll.PM100DGetBeamDiameter(byref(self.taskHandle), c_int16(self.attributeValue), None, byref(retValue))
        SMELLIELogger.debug('SNODROP DEBUG: PowerMeter.get_beam_diameter() = {}'.format(retValue.value))
        return retValue.value

    @raise_on_error_code
    def get_power(self):
        """
        :undocumented
        """
        retValue = c_double()
        dll.PM100DMeasurePower(byref(self.taskHandle), None, byref(retValue))
        SMELLIELogger.debug('SNODROP DEBUG: PowerMeter.get_power() = {}'.format(retValue.value))
        return retValue.value
        
    @raise_on_error_code
    def get_mean_power(self, nsamples, samplingRate):
        """
        :undocumented
        """
        #int32_t __cdecl MeanPower(uintptr_t *instrumentHandle, int32_t Samples, int64_t SamplingRateHz, double *mean, double *standardDeviation, double *maxRange);

        retMean = c_double()
        retSD = c_double()
        retRange = c_double()
        if nsamples>0 and samplingRate>0 and samplingRate<12:
            retValue = dll.MeanPower(byref(self.taskHandle), c_int32(nsamples), c_int64(samplingRate), byref(retMean), byref(retSD), byref(retRange))
            if retValue!=0: 
                raise PowerMeterDLLError('Power meter cannot sample this fast. Select a slower rate. {}'.format(retValue))
        else:
            raise PowerMeterLogicError('Selected sampling rate too fast. Must be <10Hz.')
        SMELLIELogger.debug('SNODROP DEBUG: PowerMeter.get_mean_power = {},{},{}'.format(retMean.value, retSD.value, retRange.value))
        return retMean.value, retSD.value, retRange.value
        
    @raise_on_error_code
    def get_wavelength(self):
        """
        :undocumented
        """
        retValue = c_double()
        dll.PM100DGetWavelength(byref(self.taskHandle), c_int16(self.attributeValue), None, byref(retValue))
        SMELLIELogger.debug('SNODROP DEBUG: PowerMeter.get_wavelength = {}'.format(retValue.value))
        return retValue.value
        
    @raise_on_error_code
    def get_power_range(self):
        """
        :undocumented
        """
        retValue = c_double()
        dll.PM100DGetPowerRange(byref(self.taskHandle), c_int16(self.attributeValue), None, byref(retValue))
        SMELLIELogger.debug('SNODROP DEBUG: PowerMeter.get_power_range = {}'.format(retValue.value))
        return retValue.value
        
    @raise_on_error_code
    def get_dark_offset(self):
        """
        :undocumented
        """
        retValue = c_double()
        dll.PM100DGetDarkOffset(byref(self.taskHandle), None, byref(retValue))
        SMELLIELogger.debug('SNODROP DEBUG: PowerMeter.get_dark_offset() = {}'.format(retValue.value))
        return retValue.value
        
    @raise_on_error_code
    def set_dark_offset_cancel(self):
        """
        :undocumented
        """
        SMELLIELogger.debug('SNODROP DEBUG: PowerMeter.set_dark_offset_cancel()')
        dll.PM100DCancelDarkAdjustment(byref(self.taskHandle), None)
        
    @raise_on_error_code
    def set_dark_offset(self):
        """
        :undocumented
        """
        SMELLIELogger.debug('SNODROP DEBUG: PowerMeter.set_dark_offset()')
        dll.PM100DStartDarkOffsetAdjustment(byref(self.taskHandle), None)

    @raise_on_error_code
    def set_wavelength(self, setValue):
        """
        :undocumented
        """
        SMELLIELogger.debug('SNODROP DEBUG: PowerMeter.set_wavelength({})'.format(setValue))
        setValue = c_double(setValue)
        dll.PM100DSetWavelength(byref(self.taskHandle), setValue, None)
        
    @raise_on_error_code
    def set_average_count(self, setValue):
        """
        :undocumented
        """
        SMELLIELogger.debug('SNODROP DEBUG: PowerMeter.set_average_count({})'.format(setValue))
        setValue = c_int16(setValue)
        dll.PM100DSetAverageCount(byref(self.taskHandle), setValue, None)
        
    @raise_on_error_code
    def get_average_count(self):
        """
        :undocumented
        """
        retValue = c_int16()
        dll.PM100DGetAverageCount(byref(self.taskHandle), None, byref(retValue))
        SMELLIELogger.debug('SNODROP DEBUG: PowerMeter.get_average_count() = {}'.format(retValue.value))
        return retValue.value
    
    @raise_on_error_code
    def default_settings(self):
        """   
        :returns: ctype string buffer, the size of which is set in :mod:config
        """
        SMELLIELogger.debug('SNODROP DEBUG: PowerMeter.default_settings()')
        self.set_average_count(100)
        self.set_wavelength(400)
        ##PM100DSetAttenuation
        #PM100DSetBeamDiameter
        #PM100DSetDateAndTime
        setDisplayBrightness(self.taskHandle,0)
        setDisplayContrast(self.taskHandle,0.5)
        #PM100DSetLineFrequency
        ##PM100DSetPhotodiodeInputFilterState
        ##PM100DSetPhotodiodeResponsivity
        #PM100DSetPowerAutorangeMode
        ##PM100DSetPowerReferenceState
        ##PM100DSetPowerReference
        setPowerUnit(self.taskHandle,0)
        ##PM100DSetPyrosensorResponsivity
        ##PM100DSetThermopileResponsivity

    @raise_on_error_code
    def identificationQuery(self):
        """
        :undocumented
        """
        firmwareRevision = create_string_buffer(PM_STR_BUFFER_SIZE)
        serialNumber = create_string_buffer(PM_STR_BUFFER_SIZE)
        manufacturerName = create_string_buffer(PM_STR_BUFFER_SIZE)
        deviceName = create_string_buffer(PM_STR_BUFFER_SIZE)
        dll.PM100DIdentificationQuery(byref(self.taskHandle), firmwareRevision, serialNumber, None, manufacturerName, deviceName, c_int32(PM_STR_BUFFER_SIZE), c_int32(PM_STR_BUFFER_SIZE), c_int32(PM_STR_BUFFER_SIZE), c_int32(PM_STR_BUFFER_SIZE) )
        return firmwareRevision.value, serialNumber.value, manufacturerName.value, deviceName.value
        
    def is_connected(self):
        """   
        Check if the connection to the device is open
        """
        return self.isConnected
        
    def is_alive(self):
        """
        Quick check alive or not.
        """
        isAlive = None
        if self.isConnected:
            firmwareRevision, serialNumber, manufacturerName, deviceName = self.identificationQuery() #choose to check the HW model:
        else: 
            self.port_open(iDQueryDoQuery=0, resetDevice=0)
            firmwareRevision, serialNumber, manufacturerName, deviceName = self.identificationQuery()
            self.port_close()   
        if (manufacturerName+deviceName == 'ThorlabsPM100D'): isAlive = True
        else: isAlive = False
        return isAlive
        
    def current_state(self):
        """
        Returns a formatted string with the current hardware settings
        """
        return "ID: {}, SelfTest: {}, PowerUnit: {}(0=W,1=dB), PowerReference: {}, ReferenceState:{}, AutorangeMode: {}, SensorInformation: {}\
        , PhotodiodeFilterState:{}, CalibrationMessage:{}, Attenuation: {}, DarkAdjustmentState: {}, DarkOffset: {}, PhotodiodeResponsivity: {}, ThermopileResponsivity: {}, PyrosensorResponsivity: {}, \
        BeamDiameter: {}, Wavelength: {}".format(
           self.identificationQuery(),
           selfTest(self.taskHandle),
           getPowerUnit(self.taskHandle),
           getPowerReference(self.taskHandle, self.attributeValue),
           getPowerReferenceState(self.taskHandle),
           getPowerAutorangeMode(self.taskHandle),
           getSensorInformation(self.taskHandle),
           getPhotodiodeInputFilterState(self.taskHandle),
           getCalibrationMessage(self.taskHandle),
           getAttenuation(self.taskHandle, self.attributeValue),
           getDarkAdjustmentState(self.taskHandle),
           self.get_dark_offset(),
           getPhotodiodeResponsivity(self.taskHandle, self.attributeValue),
           getThermopileResponsivity(self.taskHandle, self.attributeValue),
           getPyrosensorResponsivity(self.taskHandle, self.attributeValue),
           self.get_beam_diameter(), 
           self.get_wavelength())
