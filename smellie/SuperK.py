from time import sleep
from ctypes import Structure, OleDLL, create_string_buffer, c_char_p, c_double, c_int16, c_int32, c_uint16, c_uint32, c_uint8,byref
from smellie_config import SK_COM_PORT, SK_DLL_PATH, SK_STR_BUFFER_SIZE, SK_MAX_INT_FREQUENCY
from functools import wraps
import os

"""
Core functions for use in the SuperK package - not intended for use outside.
"""

class statusBitStructure(Structure):
        _fields_ = [("bit0", c_int16),("bit1", c_int16),("bit2", c_int16),("bit3", c_int16),("bit4", c_int16),("bit5", c_int16), ("bit6", c_int16),("bit7", c_int16),("bit8", c_int16),("bit9", c_int16),("bit10", c_int16),("bit11", c_int16),("bit12", c_int16),("bit13", c_int16),("bit14", c_int16),("bit15", c_int16)]

class superKControlStructure(Structure):
        _fields_ = [("trigLevelSetpointmV", c_uint16),("displayBacklightPercent", c_uint8),("trigMode", c_uint8),("internalPulseFreqHz", c_uint16),("burstPulses", c_uint16),("watchdogIntervalSec", c_uint8),("internalPulseFreqLimitHz", c_uint32)]

# for loading NI LV dll's see NI white paper http://www.ni.com/white-paper/8911/en/
# http://digital.ni.com/public.nsf/allkb/A3804F88FCDB1E6286257CE00043C1A7
# https://decibel.ni.com/content/docs/DOC-9076
# https://decibel.ni.com/content/docs/DOC-9079

def string_buffer():
    """   
    :returns: ctype string buffer, the size of which is set in :mod:config
    """
    return create_string_buffer(SK_STR_BUFFER_SIZE)

class SuperKDLLError(Exception):
    """
    Raised if an exception is flagged up *during* a call to the .dll
    """
    pass

class SuperKLogicError(Exception):
    """
    Raised *before* any call to the .dll if function arguments are incorrect.
    """
    pass
class SuperKHWError(Exception):
    """
    Raised if there is a problem with the hardware.
    """
    pass

# Open the .dll on import
if not os.path.exists(SK_DLL_PATH):
    raise SuperKLogicError("Cannot open dll on path {0}".format(SK_DLL_PATH))
try:
    dll = OleDLL(SK_DLL_PATH)
except Exception as e:
    raise SuperKLogicError("Opening dll failed! : {0}".format(str(e))) 

# Error Handling and Decoding
def decode_error(iErr):
    """
    Decodes an error code thrown by the hardware. 
    If the translation fails, this returns: unknown error code.

    :param iErr: .dll generated error code

    :returns: error message
    :type error message: string
    """
    str_buff = create_string_buffer(SK_STR_BUFFER_SIZE)
    try:
        #dll.DecodeError(c_int32(iErr), str_buff, c_int32(SK_STR_BUFFER_SIZE) )
        return str_buff.value
    except WindowsError:
        return "SuperK Library: unknown error code {0}".format(iErr)

def raise_on_error_code(in_function):
    """
    OleDll automatically detects a non-zero exit code and throws a WindowsException.
    This decorator produces a modified function that catches this, extracts and translates the error code, and throws a SuperKDLLError.

    :param in_function: the function to wrap

    :returns: a logically equivalent function that catches WindowsError exceptions thrown by ctypes, extracts and decodes the error code then re-throws as SepiaDLLError
    """
    @wraps(in_function)
    def modified(*args, **kwargs):
        try:
            return in_function(*args, **kwargs)
        except WindowsError as e:
            raise SuperKDLLError(decode_error(e.winerror))
    return modified

@raise_on_error_code
def portOpen(COMPort):
    """
    undocumented
    """
    dll.PortOpen(COMPort)

@raise_on_error_code
def portClose(COMPort):
    """
    undocumented
    """
    dll.PortClose(COMPort)

@raise_on_error_code
def getSuperKInfo(COMPort):
    """
    undocumented
    """
    serial = string_buffer()
    moduleType = c_int32(0)
    firmware = c_uint16(0)
    versionInfo = string_buffer()
    dll.GetSuperKInfo(COMPort, serial, SK_STR_BUFFER_SIZE, byref(moduleType), byref(firmware), versionInfo, SK_STR_BUFFER_SIZE)
    return firmware.value, versionInfo.value, format(moduleType.value,'02X'), serial.value

@raise_on_error_code
def getVariaInfo(COMPort):
    """
    undocumented
    """
    serial = string_buffer()
    moduleType = c_int32(0)
    firmware = c_uint16(0)
    versionInfo = string_buffer()
    dll.GetVariaInfo(COMPort, serial, SK_STR_BUFFER_SIZE, byref(moduleType), byref(firmware), versionInfo, SK_STR_BUFFER_SIZE)
    return firmware.value, versionInfo.value, format(moduleType.value,'02X'), serial.value

@raise_on_error_code
def getVariaReadings(COMPort):
    """
    undocumented
    """
    monitorInput = c_double(0)
    dll.GetVariaReadings(COMPort, byref(monitorInput))
    return monitorInput.value

@raise_on_error_code
def getSuperKReadings(COMPort):
    """
    undocumented
    """
    opticalPulseFreqkHz = c_double(0)
    actualInternalTrigFreqkHz = c_double(0)
    powerReadoutPercent = c_uint8(0)
    heatSinkTempC = c_double(0)
    supplyVoltagemV = c_double(0)
    displayInfo = string_buffer()
    dll.GetSuperKReadings(COMPort, byref(opticalPulseFreqkHz), byref(actualInternalTrigFreqkHz), byref(powerReadoutPercent), byref(heatSinkTempC), byref(supplyVoltagemV), displayInfo, SK_STR_BUFFER_SIZE )
    return opticalPulseFreqkHz.value, actualInternalTrigFreqkHz.value, powerReadoutPercent.value, heatSinkTempC.value, supplyVoltagemV.value, displayInfo.value

@raise_on_error_code
def getVariaStatusBits(COMPort):
    """
    undocumented
    """
    bitMaskDecimal = c_int32(0)
    bitCluster = statusBitStructure()
    dll.GetVariaStatusBits(COMPort, byref(bitMaskDecimal), bitCluster)  
    #printVariaStatusBits(bitCluster) #for use in debugging 
    
    #check for errors (not filter movement, that's checked elsewhere):
    if (bitCluster.bit5 == 1 or bitCluster.bit6 == 1 or bitCluster.bit9 == 1 or bitCluster.bit15 == 1):
        if (bitCluster.bit9 == 1):
            raise SuperKHWError('ERROR (superk.getVariaStatusBits). Error from shutter sensor on Varia output. Check shutter.')          
        else:
            raise SuperKHWError('ERROR (superk.getVariaStatusBits). System error. Check system.')
    
    return bitCluster

@raise_on_error_code
def printVariaStatusBits(bitCluster):
    """
    Prints Varia status bits. For use when debugging.
    """
    print "Varia Bit Status:"
    if (bitCluster.bit1 == 0): print "\tbit 1: OFF (Interlock Off)" 
    elif (bitCluster.bit1 == 1): print "\tbit 1: ON (Interlock Off)" 
    else: print "\tbit 1: OutOfRange (Interlock On)"
    
    if (bitCluster.bit2 == 0): print "\tbit 2: OFF (InterlockLoopIn)" 
    elif (bitCluster.bit2 == 1): print "\tbit 2: ON (InterlockLoopIn)" 
    else: print "\tbit 2: OutOfRange (InterlockLoopIn)"
    
    if (bitCluster.bit3 == 0): print "\tbit 3: OFF (InterlockLoopOut)" 
    elif (bitCluster.bit3 == 1): print "\tbit 3: ON (InterlockLoopOut)" 
    else: print "\tbit 3: OutOfRange (InterlockLoopOut)"
    
    if (bitCluster.bit5 == 0): print "\tbit 5: OFF (SupplyVoltageLow)" 
    elif (bitCluster.bit5 == 1): "\tbit 5: ON (SupplyVoltageLow)" 
    else: print "\tbit 5: OutOfRange (SupplyVoltageLow)"
    
    if (bitCluster.bit6 == 0): print "\tbit 6: OFF (ModuleTempRange)" 
    elif (bitCluster.bit6 == 1): print "\tbit 6: ON (ModuleTempRange)" 
    else: print "\tbit 6: OutOfRange (ModuleTempRange)"
    
    if (bitCluster.bit8 == 0): print "\tbit 8: OFF (ShutterSensor1)" 
    elif (bitCluster.bit8 == 1): print "\tbit 8: ON (ShutterSensor1)" 
    else: print "\tbit 8: OutOfRange (ShutterSensor1)"
    
    if (bitCluster.bit9 == 0): print "\tbit 9: OFF (ShutterSensor2)" 
    elif (bitCluster.bit9 == 1): print "\tbit 9: ON (ShutterSensor2)" 
    else: print "\tbit 9: OutOfRange (ShutterSensor2)"
    
    if (bitCluster.bit12 == 0): print "\tbit 12: OFF (Filter1Moving)" 
    elif (bitCluster.bit12 == 1): print "\tbit 12: ON (Filter1Moving)" 
    else: print "\tbit 12: OutOfRange (Filter1Moving)"
    
    if (bitCluster.bit13 == 0): print "\tbit 13: OFF (Filter2Moving)" 
    elif (bitCluster.bit13 == 1): print "\tbit 13: ON (Filter2Moving)" 
    else: print "\tbit 13: OutOfRange (Filter2Moving)"
    
    if (bitCluster.bit14 == 0): print "\tbit 14: OFF (Filter3Moving)" 
    elif (bitCluster.bit14 == 1): print "\tbit 14: ON (Filter3Moving)" 
    else: print "\tbit 14: OutOfRange (Filter3Moving)"
    
    if (bitCluster.bit15 == 0): print "\tbit 15: OFF (ErrorCodePresent)" 
    elif (bitCluster.bit15 == 1): print "\tbit 15: ON (ErrorCodePresent)" 
    else: print "\tbit 15: OutOfRange (ErrorCodePresent)"

@raise_on_error_code
def getSuperKStatusBits(COMPort):
    """
    undocumented
    """
    bitMaskDecimal = c_int32(0)
    bitCluster = statusBitStructure()
    dll.GetSuperKStatusBits(COMPort, byref(bitMaskDecimal), bitCluster)
    #printSuperKStatusBits(bitCluster) #for use in debugging
    
    #check for errors:
    if (bitCluster.bit2 == 1 or bitCluster.bit5 == 1 or bitCluster.bit6 == 1 or bitCluster.bit7 == 1):
        raise SuperKHWError('ERROR (superk.getSuperKStatusBits). System error. Check system.')
    
    return bitCluster

@raise_on_error_code
def printSuperKStatusBits(bitCluster):
    """
    Prints SuperK status bits. For use when debugging.
    """
    print "SuperK Bit Status:"

    if (bitCluster.bit0 == 0): print "\tbit 0: OFF (Emission)" 
    elif (bitCluster.bit0 == 1): print "\tbit 0: ON (Emission)" 
    else: print "\tbit 0: OutOfRange (Emission unknown)" 
    
    if (bitCluster.bit1 == 0): print "\tbit 1: OFF (Interlock off)" 
    elif (bitCluster.bit1 == 1): print "\tbit 1: ON (Interlock ON)"
    else: print "\tbit 1: OutOfRange (Interlock unknown)"
    
    if (bitCluster.bit2 == 0): print "\tbit 2: OFF (Interlock power failure)" 
    elif (bitCluster.bit2 == 1): print "\tbit 2: ON (Interlock power failure)" 
    else: print "\tbit 2: OutOfRange (Interlock power unknown)"
    
    if (bitCluster.bit3 == 0): print "\tbit 3: OFF (Interlock loop off)" 
    elif (bitCluster.bit3 == 1): print "\tbit 3: ON (Interlock loop off)" 
    else: print "\tbit 3: OutOfRange (Interlock loop unknown)"
    
    if (bitCluster.bit5 == 0): print "\tbit 5: OFF (Supply voltage low)" 
    elif (bitCluster.bit5 == 1): print "\tbit 5: ON (Supply voltage low)" 
    else: print "\tbit 5: OutOfRange (Supply voltage unknown)"
    
    if (bitCluster.bit6 == 0): print "\tbit 6: OFF (Module temp range)" 
    elif(bitCluster.bit6 == 1): print "\tbit 6: ON (Module temp range)" 
    else: print "\tbit 6: OutOfRange (Module temp range unknown)"
    
    if (bitCluster.bit7 == 0): print "\tbit 7: OFF (Pump temp high)" 
    elif (bitCluster.bit7 == 1): print "\tbit 7: ON (Pump temp high)" 
    else: print "\tbit 7: OutOfRange (Pump temp unknown)"
    
    if (bitCluster.bit8 == 0): print "\tbit 8: OFF (Pulse overrun)" 
    elif (bitCluster.bit8 == 1): print "\tbit 8: ON (Pulse overrun)" 
    else: print "\tbit 8: OutOfRange (Pulse overrun unknown)"
    
    if (bitCluster.bit9 == 0): print "\tbit 9: OFF (Trig signal level)" 
    elif (bitCluster.bit9 == 1): print "\tbit 9: ON (Trig signal level)" 
    else: print "\tbit 9: OutOfRange (Trig signal level unknown)"
    
    if (bitCluster.bit10 == 0): print "\tbit 10: OFF (Trig edge)" 
    elif (bitCluster.bit10 == 1): print "\tbit 10: ON (Trig edge)" 
    else: print "\tbit 10: OutOfRange (Trig edge unknown)"
    
    if (bitCluster.bit15 == 0): print "\tbit 15: OFF (Error code present)" 
    elif (bitCluster.bit15 == 1): print "\tbit 15: ON (Error code present)" 
    else: print "\tbit 15: OutOfRange (Error code present unknown)"

@raise_on_error_code
def getSuperKControls(COMPort):
    """
    undocumented
    """
    controlCluster = superKControlStructure()
    dll.GetSuperKControls(COMPort, controlCluster)
    return controlCluster

@raise_on_error_code
def getVariaControls(COMPort):
    """
    undocumented
    """
    NDFilterSetpointPercentx10 = c_uint16(0) #not used
    SWPFilterAngstrom = c_uint16(0)
    LWPFilterAngstrom = c_uint16(0)
    dll.GetVariaControls(COMPort, byref(NDFilterSetpointPercentx10), byref(SWPFilterAngstrom), byref(LWPFilterAngstrom))
    return SWPFilterAngstrom.value, LWPFilterAngstrom.value

@raise_on_error_code
def setSuperKControls(COMPort,controlCluster):
    """
    undocumented
    """
    #the superK firmware checks set value and won't set any specified value which is out of range. This will be caught by the subsequent check 'get' confirming the 'set'.
    if (controlCluster.internalPulseFreqHz <= SK_MAX_INT_FREQUENCY): #do customise the maximum rate so add this check.
        dll.SetSuperKControls(COMPort, controlCluster)
    else:
        raise SuperKHWError('ERROR (superk.setSuperKControls). Specified pulse rate faster than SuperK maximum (20k).')     
        
@raise_on_error_code
def setSuperKControlEmission(COMPort,state):
    """
    Sets the SuperK emission.
    """
    waitTime = 3 #wait time for emission to switch (can take a few seconds)
    superKBitCluster = getSuperKStatusBits(COMPort)
    variaBitCluster = getVariaStatusBits(COMPort)
    
    dll.SetSuperKControlEmission(COMPort, c_uint8(state) )
    sleep(waitTime) #wait for emission to switch
    superKBitCluster = getSuperKStatusBits(COMPort)
    if (superKBitCluster.bit15 == 1): #if superK status bit15 tripped due to interlock, it should have cleared. If it hasn't here, it must be another error so stop. 
        dll.SetSuperKControlEmission(COMPort, c_uint8(0) )
        raise SuperKHWError('ERROR (superk.setSuperKControlEmission). System error. Emission state unknown. Check system.')

@raise_on_error_code
def setSuperKControlInterlock(COMPort,state):
    """
    Sets the SuperK internal interlock. Checks for hardware errors before doing so. Checks if external interlock is unlocked before unlocking laser.
    If laser is locked while emission is on, HW will report a warning (SuperK status bit 15 on).
    setting interlock to 1 unlocks laser (status bit1 reads 0 for interlock off)
    setting interlock to 0 locks laser (status bit1 reads 1 for interlock on)
    """
    bitCluster = getSuperKStatusBits(COMPort)
    if (bitCluster.bit2 == 0 and bitCluster.bit5 == 0 and bitCluster.bit6 == 0 and bitCluster.bit7 == 0): #check for system errors (not bit 15 which occurs if external interlock had been tripped while unlocked or running)
        if (state==1 and bitCluster.bit3 == 0): #only unlock if external interlock is already unlocked.
            dll.SetSuperKControlInterlock(COMPort, c_uint8(state))
        elif (state==1 and bitCluster.bit3 == 1):
            raise SuperKLogicError('ERROR (superk.setSuperKControlInterlock): Ensure interlock circuit is unlocked before unlocking laser.')
        if (state==0):
            dll.SetSuperKControlInterlock(COMPort, c_uint8(state))
    elif (bitCluster.bit2 == 1):
        raise SuperKHWError('ERROR (superk.setSuperKControlInterlock): Interlock power failure. Check system.')
    else:
        raise SuperKHWError('ERROR (superk.setSuperKControlInterlock). Unable to set interlock due to system error. Check system.')

@raise_on_error_code
def setVariaControls(COMPort, SWPFilterAngstrom, LWPFilterAngstrom):
    variaBitCluster = getVariaStatusBits(COMPort)
    #superKBitCluster = getSuperKStatusBits(COMPort)
    #if (superKBitCluster.bit0 == 0 or superKBitCluster.bit0 == 1 ): #require emission to be OFF (this needs discussing, I think it's ok to leave o.)
    if (variaBitCluster.bit15 == 0): #require no error (bit15 'general' error bit),
        if (SWPFilterAngstrom > LWPFilterAngstrom): #require high > low wavelength
            if ((SWPFilterAngstrom - LWPFilterAngstrom) >= 100 and (SWPFilterAngstrom - LWPFilterAngstrom) <= 1000): # check wavelength difference is >10nm and <100nm (min and max bandwidth spec'd by manufacturer)
                if (SWPFilterAngstrom <= 8400 and LWPFilterAngstrom >= 4000):
                    dll.SetVariaControls(COMPort, c_uint16(0), c_uint16(SWPFilterAngstrom), c_uint16(LWPFilterAngstrom))
                    variaBitCluster = getVariaStatusBits(COMPort)
                    
                    #now test to see if filters are moving. 30sec is about the time for the largest possible move (give a bit longer)
                    #function keeps running until they have stopped moving (blocking other functions until so)
                    for x in range(71):
                        if (variaBitCluster.bit12 == 1 or variaBitCluster.bit13 == 1 or variaBitCluster.bit14 == 1): #check all filter movement sensors
                            sleep(0.5)
                            variaBitCluster = getVariaStatusBits(COMPort)
                            if (variaBitCluster.bit12 == 0 and variaBitCluster.bit13 == 0 and variaBitCluster.bit14 == 0):
                                break
                        if (x >= 70):
                            raise SuperKLogicError( 'ERROR (superk.setVariaControls): Filters have not stopped moving after a long time. Check system.')
                else:
                    raise SuperKLogicError( 'ERROR (superk.setVariaControls): Cannot set to specified values. Minimum LWP wavelength is 400nm. Maximum SWP wavelength is 840nm (with 10nm <= BW <= 100nm).')
            else:
                raise SuperKLogicError( 'ERROR (superk.setVariaControls): Minimum bandwidth is 10nm. Maximum bandwidth is 100nm. SP & LP filters must differ by at least 10nm and no more than 100nm.')
        else:
            raise SuperKLogicError( 'ERROR (superk.setVariaControls): SWP filter value must be larger than LWP filter value')
    else:
        raise SuperKLogicError( 'ERROR (superk.setVariaControls): Setting Varia Filters: ERROR present. Filters not set. Check system.')
    #else:
    #    raise SuperKLogicError( 'Setting Varia Filters: ERROR: Emission is ON. Cannot adjust wavelength without turning off emission.')
