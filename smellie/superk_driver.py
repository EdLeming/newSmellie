from smellie_config import SK_COM_PORT, TRIG_GEN_MAX_FREQUENCY
from varia_ndfilter import VariaNDFilter
from time import sleep
from superk import string_buffer, portOpen, portClose, getSuperKInfo, getVariaInfo, getSuperKStatusBits, getVariaStatusBits, setSuperKControlEmission, setSuperKControlInterlock, setSuperKControls, getSuperKControls, setVariaControls, getVariaControls, statusBitStructure, superKControlStructure
from smellie.smellie_logger import SMELLIELogger

from ctypes import c_uint32, c_uint16, c_uint8

class SuperKDriverLogicError(Exception):
    """
    Thrown if an inconsistency is noticed *before* any instructions are sent to the hardware (i.e. a problem with code logic)
    """
    pass

class SuperKDriverHWError(Exception):
    """
    Thrown if an inconsistency is noticed *after* any hardware instruction is executed (i.e. a problem with the hardware itself)
    """
    pass

class SuperKDriver(object):

    def __init__(self):
        self.COMPort = SK_COM_PORT
        self.NDFilter = VariaNDFilter()
        self.isConnected = False
        
    def port_open(self):
        """
        undocumented
        """
        SMELLIELogger.debug('SNODROP DEBUG: SuperKDriver.port_open()')
        if not self.isConnected:
            portOpen(self.COMPort) #open SuperK
            self.NDFilter.port_open() #open varia ND filter arduino motor controller
            self.isConnected = True
            self.set_parameters() #load default settings
        else:
            raise SuperKDriverLogicError("Laser port already open.") 

    def port_close(self):
        """
        undocumented
        """
        SMELLIELogger.debug('SNODROP DEBUG: SuperKDriver.port_close()')
        if self.isConnected:
            portClose(self.COMPort) #close SuperK
            self.NDFilter.port_close() #close varia ND filter controller
            self.isConnected = False
        else:
            raise SuperKDriverLogicError("SuperK port not open.")
            
    def get_superK_status(self):
        """
        Check the status of the SuperK Laser status bits.
        
        :returns: superk status bits
        """
        if self.isConnected:
            superKStatus = getSuperKStatusBits(self.COMPort)
            SMELLIELogger.debug('SNODROP DEBUG: SuperKDriver.get_superK_status()')
            #check if any errors are present. If so, log and throw exception.
            if (superkStatus.bit2==1 or superkStatus.bit5==1 or superkStatus.bit6==1 or superkStatus.bit7==1 or superkStatus.bit8==1 or superkStatus.bit9==1 or superkStatus.bit10==1 or superkStatus.bit15==1):
                SMELLIELogger.warn('SNODROP WARN: SuperKDriver.get_superK_status()')
                raise SuperKDriverHWError("Error reported in SuperK status bits. Check system.")
            return superKStatus
        else:
            raise SuperKDriverLogicError("SuperK port not open.")
            return 0
        
    def get_varia_status(self):
        """
        Check the status of the SuperK Varia status bits.
        
        :returns: varia status bits
        """
        if self.isConnected:
            variaStatus = getvariaStatusBits(self.COMPort)
            SMELLIELogger.debug('SNODROP DEBUG: SuperKDriver.get_varia_status()')
            #check if any errors are present. If so, log and throw exception.
            #variaStatus.bit8 is the shutter of the infrared outlet of the Varia which is blanked off (option provided by manufacturer which we don't use). Sensor indicator works but has no relevance for our use.
            if (variaStatus.bit5==1 or variaStatus.bit6==1 or variaStatus.bit9==1 or variaStatus.bit15==1):
                SMELLIELogger.warn('SNODROP WARN: Error reported in SuperK status bits. Check system.')
                raise SuperKDriverHWError("Error reported in SuperK status bits. Check system.")
            return variaStatus
        else:
            raise SuperKDriverLogicError("SuperK port not open.")
            return 0

    def set_parameters(self, trig_mode=1, pulse_rate=0):
        """
        set superK control parameters. Most of these should not be configurable and hard-coded for safety.
        """
        if self.isConnected:
            SMELLIELogger.debug('SNODROP DEBUG: SuperKDriver.set_parameters({},{})'.format(trig_mode,pulse_rate))
            if (trig_mode<=1):
                if (pulse_rate<=TRIG_GEN_MAX_FREQUENCY):
                    superKControls = superKControlStructure()
                    superKControls.trigLevelSetpointmV = c_uint16(1000)
                    superKControls.displayBacklightPercent = c_uint8(0)
                    superKControls.trigMode = c_uint8(trig_mode)
                    superKControls.internalPulseFreqHz = c_uint16(pulse_rate)
                    superKControls.burstPulses = c_uint16(1) 
                    superKControls.watchdogIntervalSec = c_uint8(0)
                    superKControls.internalPulseFreqLimitHz = c_uint32(24000) #doesn't do anything. Possibly a manufacturer option disabled in firmware.
                    setSuperKControls(self.COMPort,superKControls)

                    #check parameters have been set correctly:
                    new_superKControls=self.get_parameters()
                    if (superKControls.trigLevelSetpointmV!=new_superKControls.trigLevelSetpointmV or
                    superKControls.displayBacklightPercent!=new_superKControls.displayBacklightPercent or
                    superKControls.trigMode!=new_superKControls.trigMode or
                    superKControls.internalPulseFreqHz!=new_superKControls.internalPulseFreqHz or 
                    superKControls.burstPulses!=new_superKControls.burstPulses or 
                    superKControls.watchdogIntervalSec!=new_superKControls.watchdogIntervalSec or 
                    superKControls.internalPulseFreqLimitHz!=new_superKControls.internalPulseFreqLimitHz):
                        SMELLIELogger.warn('SNODROP WARN: Error upon setting SuperK control bits. Specified values have not all been set. Check system.')
                        raise SuperKDriverHWError("Error upon setting SuperK control bits. Specified values have not all been set. Check system.{}.") 

                    #sending warning about change of trigger mode.
                    if superKControls.trigMode==0:
                        SMELLIELogger.notice('SNODROP NOTICE: Trigger is set to INTERNAL. Rate is set to {}.'.format(new_superKControls.internalPulseFreqHz))
                    elif superKControls.trigMode==1:
                        SMELLIELogger.notice('SNODROP NOTICE: Trigger is set to EXTERNAL.')
                else:
                    SMELLIELogger.warn('SNODROP WARN: Specified pulse rate faster than maximum in config file.')
                    raise SuperKDriverLogicError("Specified pulse rate faster than maximum in config file. Check settings and config file.") 
            else:
                SMELLIELogger.warn('SNODROP WARN: This trigger mode not enabled.')
                raise SuperKDriverLogicError("This SuperK trigger mode not enabled.") 
        else:
            raise SuperKDriverLogicError("SuperK port not open.")
            
    def get_parameters(self):
        """
        undocumented
        """
        if self.isConnected:
            superKControlStructure = getSuperKControls(self.COMPort)
            SMELLIELogger.debug('SNODROP DEBUG: SuperKDriver.get_parameters()')
            return superKControlStructure
        else:
            raise SuperKDriverLogicError("SuperK port not open.")
            return 0

    def set_trigger_mode(self, set_mode=1, set_internal_trigger_rate=0):
        """
        undocumented
        """
        if self.isConnected:
            SMELLIELogger.debug('SNODROP DEBUG: SuperKDriver.set_trigger_mode({},{})'.format(set_mode,set_internal_trigger_rate))
            self.set_parameters(trig_mode=set_mode, pulse_rate=set_internal_trigger_rate)
        else:
            raise SuperKDriverLogicError("SuperK port not open.")

    def get_trigger_mode(self):
        """
        undocumented
        """
        if self.isConnected:
            superKControlStructure = self.get_parameters()
            SMELLIELogger.debug('SNODROP DEBUG: SuperKDriver.get_trigger_mode() = {}'.format(superKControlStructure.trigMode))
            return superKControlStructure.trigMode #for simplicity, just return mode, not internal trigger rate. Rate should always be set.
        else:
            raise SuperKDriverLogicError("SuperK port not open.")
    
    def get_wavelengths(self):
        """
        undocumented
        """
        if self.isConnected:
            high_wavelength, low_wavelength = getVariaControls(self.COMPort)
            SMELLIELogger.debug('SNODROP DEBUG: SuperKDriver.get_wavelengths() = {}, {}'.format(low_wavelength, high_wavelength))
            return low_wavelength, high_wavelength
        else:
            raise SuperKDriverLogicError("SuperK port not open.")
            return 0
    
    def set_wavelengths(self, set_low_wavelength, set_high_wavelength):
        """
        Set the low and high wavelengths of the Varia (checking if the settings aren't already set)
        """
        if self.isConnected:
            # set the low and high wavelengths of the Varia (checking if the settings aren't already set)
            SMELLIELogger.debug('SNODROP DEBUG: SuperKDriver.set_wavelengths({},{})'.format(set_low_wavelength, set_high_wavelength))
            low_wavelength, high_wavelength = self.get_wavelengths()
            if (set_low_wavelength!=low_wavelength or set_high_wavelength!=high_wavelength):
                setVariaControls(self.COMPort,set_high_wavelength,set_low_wavelength)
                low_wavelength, high_wavelength = self.get_wavelengths()
                #check values set correctly,
                if (set_low_wavelength!=low_wavelength or set_high_wavelength!=high_wavelength):
                    raise SuperKDriverLogicError("SuperK Varia wavelengths not set correctly.")
        else:
            raise SuperKDriverLogicError("SuperK port not open.")

    def is_interlock_locked(self):
        """
        Check the status of the SMELLIE interlock.
        
        :returns: True if the interlock is Locked (Relay Open)
        """
        if self.isConnected:
            SMELLIELogger.debug('SNODROP DEBUG: SuperKDriver.is_laser_locked()')
            #interlock circuit
            superKStatus = getSuperKStatusBits(self.COMPort)
            if (superKStatus.bit3 == 0):
                interlock_locked = False
            elif (superKStatus.bit3 == 1):
                interlock_locked = True
            else:
                raise SuperKDriverLogicError("Unknown response for interlock value.")
                interlock_locked = None
        return interlock_locked
            
    def is_laser_locked(self):
        """
        Poll the SuperK driver for its lock status.
        
        :returns: True if the internal-lock is on.
        """
        if self.isConnected:
            SMELLIELogger.debug('SNODROP DEBUG: SuperKDriver.is_laser_locked()')
            
            #interlock circuit
            interlock_locked = self.is_interlock_locked()

            #internal interlock
            superKStatus = getSuperKStatusBits(self.COMPort)
            if (superKStatus.bit1 == 0):
                laser_locked = False
            elif (superKStatus.bit1 == 1):
                laser_locked = True
            else:
                raise SuperKDriverLogicError("Unknown response for interlock value.")
                interlock_locked = None

            #combination of external interlock and SuperK internal interlock
            if (laser_locked or interlock_locked):
                is_locked = True
                SMELLIELogger.notice('SNODROP NOTICE: SuperK laser locked.')
            elif (laser_locked==False and interlock_locked==False):
                is_locked = False
                SMELLIELogger.notice('SNODROP NOTICE: SuperK laser unlocked.')
            else:
                SMELLIELogger.warn('SNODROP WARN: Unknown SuperK laser lock state. Check system.')
                raise SuperKDriverLogicError("Unknown response for interlock value.")
                is_locked = None
            return is_locked
        else:
            raise SuperKDriverLogicError("SuperK port not open.") 
            return None
            
    def set_laser_lock(self, set_locked = True):
        """
        Set the superK internal lock.
        """
        if self.isConnected:
            SMELLIELogger.debug('SNODROP DEBUG: SuperKDriver.set_laser_lock({})'.format(set_locked))
            if set_locked != self.is_laser_locked():
                if set_locked==True:
                    setSuperKControlInterlock(self.COMPort,0) #setting interlock to 0 locks laser
                elif set_locked==False:
                    setSuperKControlInterlock(self.COMPort,1) #setting interlock to 1 unlocks laser
                #check value was set correctly
                if set_locked != self.is_laser_locked():
                    raise SuperKDriverLogicError("SuperK interlock not set correctly.")
        else:
            raise SuperKDriverLogicError("SuperK port not open.")

    def is_emission_on(self):
        """
        Check the status of the SuperK emission.
        
        :returns: True if the emission is on (pulsing or ready to pulse).
        """
        if self.isConnected:
            SMELLIELogger.debug('SNODROP DEBUG: SuperKDriver.is_emission_on()')
            superKStatus = getSuperKStatusBits(self.COMPort)
            if (superKStatus.bit0 == 0):
                emission_on = False
                SMELLIELogger.notice('SNODROP NOTICE: SuperK laser emission OFF.')
            elif (superKStatus.bit0 == 1):
                emission_on = True
                SMELLIELogger.notice('SNODROP NOTICE: SuperK laser emission ON.')
            else:
                SMELLIELogger.warn('SNODROP WARN: Unknown SuperK laser emission state. Check system.')
                raise SuperKDriverLogicError("Unknown response for emission value.")
                emission_on = None
        return emission_on

    def set_laser_emission(self, set_emission = False):
        """
        Set the superK emission (laser pulses if triggered - either by its own trigger or an external trigger, as set in the trigger settings).
        """
        if self.isConnected:
            SMELLIELogger.debug('SNODROP DEBUG: SuperKDriver.set_laser_emission({})'.format(set_emission))
            if set_emission != self.is_emission_on():
                if (set_emission==True and self.is_laser_locked() == False): #laser must be unlocked before turning emission on
                    setSuperKControlEmission(self.COMPort,1) #setting interlock to 1 turns emission on
                elif (set_emission==True and self.is_laser_locked() == True):
                    raise SuperKDriverLogicError("Interlocks must be unlocked before SuperK emission can be set.")
                if set_emission==False: #turn emission off
                    setSuperKControlEmission(self.COMPort,0) #setting emission to 0 turns emission off
                #check emission was set correctly
                if set_emission != self.is_emission_on():
                    raise SuperKDriverLogicError("SuperK emission not set correctly.")
        else:
            raise SuperKDriverLogicError("SuperK port not open.")

    def go_ready(self, step_number, low_wavelength, high_wavelength):
        """
        undocumented
        """
        if self.isConnected:
            SMELLIELogger.debug('SNODROP DEBUG: SuperKDriver.go_ready({},{},{})'.format(step_number, low_wavelength, high_wavelength))
            
            trigger_mode = self.get_trigger_mode()
            if trigger_mode==1:
                SMELLIELogger.warn('SNODROP WARN: SuperK laser being armed. Ready to pulse when triggered externally.')
            elif trigger_mode==0:
                for x in range(6):
                    SMELLIELogger.warn('SNODROP WARN: SuperK laser being armed. Laser will pulse with internal trigger. In {} seconds...'.format(5-x))
                    sleep(1)

            # set the wavelengths of the Varia
            self.set_wavelengths(low_wavelength,high_wavelength)
            
            # set the Varia ND filter (the step number to the stepper motor controller)
            #NDFilter_set_position(step_number)
            
            # turn the lock off then turn the emission on (in this order)
            self.set_laser_lock(False)
            self.set_laser_emission(True)
        else:
            raise SuperKDriverLogicError("SuperK port not open.")
            
    def go_safe(self):
        """
        undocumented
        """
        if self.isConnected:
            SMELLIELogger.debug('SNODROP DEBUG: SuperKDriver.go_safe()')
            # turn the emission off then turn the emission on (in this order)
            self.set_laser_emission(False)
            self.set_laser_lock(True)
            # re-apply safe settings (external trigger etc.)
            self.set_parameters()
            SMELLIELogger.warn('SNODROP WARN: SuperK laser being set to safe mode.')
        else:
            raise SuperKDriverLogicError("SuperK port not open.")

    def varia_go_safe(self):
        """
        undocumented
        """
        if self.isConnected:
            SMELLIELogger.debug('SNODROP DEBUG: SuperKDriver.varia_go_safe()')
            # set varia wavelengths to be beyond the 700nm filter (so light is filtered out)
            low_wavelength, high_wavelength = getVariaControls(self.COMPort)
            if (low_wavelength!=7900 and high_wavelength!=8000):
                setVariaControls(self.COMPort,8000,7900)
        else:
            raise SuperKDriverLogicError("SuperK port not open.")
            
    def get_identity(self):
        """
        undocumented
        """
        if self.isConnected:
            firmware, version_info, module_type, serial_number = getSuperKInfo(self.COMPort)
            superK_info = "Firmware: {} Version Info: {} Module Type: {} Serial Number: {}".format( firmware, version_info, module_type, serial_number )
            firmware, version_info, module_type, serial_number = getVariaInfo(self.COMPort)
            varia_info = "Firmware: {} Version Info: {} Module Type: {} Serial Number: {}".format( firmware, version_info, module_type, serial_number )
            SMELLIELogger.debug('SNODROP DEBUG: SuperKDriver.get_identity() = {},{}'.format(superK_info, varia_info))
            return superK_info, varia_info
        else:
            raise SuperKDriverLogicError("SuperK port not open.")
            return 0
        
    #upon open, move until home status. then move up to step -300. set reference (moving away from home - noted for backlash).
    #set position increases position, but for a change in direction, reverse direction plus an addition 30 steps, then reverse direction again and go forward 30 steps. Backlash in both directions hopefully cancel.
    def NDFilter_position(self):
        NDFilterPosition = self.NDFilter.get_position()
        SMELLIELogger.debug('SNODROP DEBUG: SuperKDriver.NDFilter_position() = {}'.format(NDFilterPosition))
        return NDFilterPosition
        
    def NDFilter_set_position(self, positionValue):
        SMELLIELogger.debug('SNODROP DEBUG: SuperKDriver.NDFilter_set_position({})'.format(positionValue))
        self.NDFilter.set_position(positionValue)
        
    def NDFilter_get_home_status(self):
        NDFilterHomeStatus = self.NDFilter.get_home_status()
        SMELLIELogger.debug('SNODROP DEBUG: SuperKDriver.NDFilter_get_home_status() = {}'.format(NDFilterHomeStatus))
        return NDFilterHomeStatus
        
    def NDFilter_set_reference(self):
        SMELLIELogger.debug('SNODROP DEBUG: SuperKDriver.NDFilter_set_reference()')
        self.NDFilter.set_reference_position()
        return 0
        
    def is_connected(self):
        """
        Check if the connection to the device is open
        """
        SMELLIELogger.debug('SNODROP DEBUG: SuperKDriver.is_connected() = {}'.format(self.isConnected))
        return self.isConnected
        
    def is_alive(self):
        """
        Quick check alive or not.
        """
        if self.isConnected:
            checkValue = getSuperKInfo(self.COMPort) #check superK Compact HW model ('74')
            checkValue2 = getVariaInfo(self.COMPort) #check superK Varia HW model ('68')
            checkValue3 = self.NDFilter.is_alive() #check variamotor controller
            if (checkValue[2] == '74' and checkValue2[2] == '68' and checkValue3 == True): isAlive = True
            else: isAlive = False
            SMELLIELogger.debug('SNODROP DEBUG: SuperKDriver.is_alive() = {}'.format(isAlive))
            return isAlive
        else:
            raise SuperKDriverLogicError("SuperK port not open.") 
            return 0 

    def system_state(self):
        """
        Returns a formatted string with the hardware info and constant settings.
        """
        if self.isConnected:
            superK_info, varia_info = self.get_identity()
            SMELLIELogger.debug('SNODROP DEBUG: SuperKDriver.system_state() = {}, {}, {}'.format(superK_info, varia_info, self.NDFilter.system_state() ))
            return "SuperK laser (settings):: Compact Info: {}, Varia Info: {}{}".format(superK_info, varia_info, self.NDFilter.system_state() )
        else:
            raise SuperKDriverLogicError("SuperK port not open.") 
            return 0

    def current_state(self):
        """
        Returns a formatted string with the current hardware settings
        """
        if self.isConnected:
            low_wavelength, high_wavelength = self.get_wavelengths()
            SMELLIELogger.debug('SNODROP DEBUG: SuperKDriver.current_state() = {},{},{}'.format(self.NDFilter.current_state(), low_wavelength, high_wavelength ))
            return "SuperK laser (settings):: NDFilter Step: {}, Low Wavelength: {}, High Wavelength: {}. {}".format(self.NDFilter.current_state(), low_wavelength, high_wavelength )
        else:
            raise SuperKDriverLogicError("SuperK port not open.") 
            return 0    
