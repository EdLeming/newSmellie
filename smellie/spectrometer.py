from smellie.spectrometer_util import string_buffer, createWrapper, destroyWrapper, openAllSpectrometers, closeAllSpectrometers, getFirmwareVersion, getName, getSerialNumber, getIntegrationTime, setIntegrationTime, getScansToAverage, setScansToAverage, getSpectrum, getWavelengths, writeSpectrum, getFeatureControllerIrradianceCalibrationFactor, getFeatureControllerExternalTriggerDelay, getExternalTriggerMode, setExternalTriggerMode, setCorrectForElectricalDark, setCorrectForDetectorNonlinearity, getBoxcarWidth, setBoxcarWidth, getMaximumIntensity, getMaximumIntegrationTime, getMinimumIntegrationTime, getNumberOfDarkPixels, getNumberOfPixels, isSaturated, getLastException, destroyExternalTriggerDelay, getExternalTriggerDelayMaximum, getExternalTriggerDelayMinimum, setExternalTriggerDelay, initialise, shutdown

class SpectrometerLogicError(Exception):
    """
    Thrown if an inconsistency is noticed *before* any instructions are sent to the hardware (i.e. a problem with code logic)
    """
    pass

class SpectrometerHWError(Exception):
    """
    Thrown if an inconsistency is noticed *after* any hardware instruction is executed (i.e. a problem with the hardware itself)
    """
    pass

class Spectrometer(object):

    def __init__(self):
        self.wrapper = createWrapper()
        self.isConnected = False

    def port_open(self):
        """   
        undocumented
        """
        if not self.isConnected:
            openAllSpectrometers(self.wrapper)
            self.isConnected = True
        else:
            raise SpectrometerLogicError("Spectrometer port already open.") 

    def port_close(self):
        """   
        undocumented
        """
        if self.isConnected:
            closeAllSpectrometers(self.wrapper)
            destroyWrapper(self.wrapper)
            self.isConnected = False
        else:
            raise SpectrometerLogicError("Spectrometer port not open.") 
        
    def get_identity(self):
        """   
        undocumented
        """
        if self.isConnected:
            return getName(self.wrapper), getFirmwareVersion(self.wrapper), getSerialNumber(self.wrapper)
        else:
            raise SpectrometerLogicError("Spectrometer port not open.") 
            return 0
        
    def is_connected(self):
        """   
        Check if the connection to the device is open
        """
        return self.isConnected
        
    def is_alive(self):
        """
        Quick check alive or not.
        """
        if self.isConnected:
            if (self.get_identity()[0] == 'USB2000+'): isAlive = True #choose to check the HW model ('USB2000+')
            else: isAlive = False
            return isAlive
        else:
            raise SpectrometerLogicError("Spectrometer port not open.") 
            return 0
        
    def system_state(self):
        """
        Returns a formatted string with the hardware info and constant settings.
        """
        if self.isConnected:
            return "Spectrometer (system):: Identity (name, Firmware, SerialNumber): {}".format( self.get_identity() )
        else:
            raise SpectrometerLogicError("Spectrometer port not open.") 
            return 0
        
    def current_state(self):
        """
        Returns a formatted string with the current hardware settings
        """
        if self.isConnected:
            return "Spectrometer (settings):: ".format( )
        else:
            raise SpectrometerLogicError("Spectrometer port not open.") 
            return 0
