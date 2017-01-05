from sepia.usb import close_usb_device, open_usb_device
from sepia.fwr import free_module_map, get_module_map, get_fwr_version
from sepia.slm import set_intensity_fine_step, get_intensity_fine_step,get_pulse_parameters, set_pulse_parameters, decode_freq_trig_mode
from sepia.com import get_module_type, decode_module_type
from sepia.scm import get_laser_locked, get_laser_soft_lock, set_laser_soft_lock
from smellie_config import PQ_DRIVER_SLOT_ID, PQ_DRIVER_DEV_ID, PQ_SLOT_ID
import time
from smellie.smellie_logger import SMELLIELogger

"""
Control of the PQ Laser Driver (Sepia II module)
"""

class PQDriverLogicError(Exception):
    """
    Thrown if an inconsistency is noticed *before* any instructions are sent to the hardware (i.e. a problem with code logic)
    """
    pass

class PQDriverHWError(Exception):
    """
    Thrown if an inconsistency is noticed *after* any hardware instruction is executed (i.e. a problem with the hardware itself)
    """
    pass

class PQDriver(object):
    """
    Controls the Laser Driver via commands sent down a USB port.
    """
    def __init__(self):
        self.dev_id  = PQ_DRIVER_DEV_ID
        self.driver_slot_id = PQ_DRIVER_SLOT_ID
        self.laser_slot_id = PQ_SLOT_ID
        self.isConnected = False

    def port_open(self):
        """
        Open the USB connection to PQ driver
        """
        SMELLIELogger.debug('SNODROP DEBUG: PQDriver.port_open()')
        if not self.isConnected:
            open_usb_device(self.dev_id)
            time.sleep(5)
            get_module_map(self.dev_id)
            time.sleep(5)
            self.isConnected = True
            
            # Sets the laser into pulse mode, with the frequency mode = rising edge of the external trigger pulse.
            # Do not change this for Detector Safety reasons!
            set_pulse_parameters(self.dev_id, self.laser_slot_id)
            time.sleep(5)
            self.check_pulse_mode()
            self.check_trig_mode()
        else:
            raise PQDriverLogicError("Laser port already open.") 

    def port_close(self):
        """
        (Cleanly!) close the USB connection to the Sepia driver
        """
        SMELLIELogger.debug('SNODROP DEBUG: PQDriver.port_close()')
        if self.isConnected:
            free_module_map(self.dev_id)
            time.sleep(5)
            close_usb_device(self.dev_id)
            time.sleep(5) #give this some time, otherwise run into USB device errors on next open.
            self.isConnected = False
        else:
            raise PQDriverLogicError("Laser port not open.") 

    def get_pulse_params(self):
        """
        Poll the Sepia driver for a summary of the current device parameters: frequency mode, pulse mode and head type

        :returns: frequency_mode
        :returns: pulse_mode 
        :returns: head_type
        :rtype: (int, bool, int) tuple
        """
        if self.isConnected:
            params = get_pulse_parameters(self.dev_id, self.laser_slot_id)
            SMELLIELogger.debug('SNODROP DEBUG: PQDriver.get_pulse_params() = {}'.format(params))
            return params
        else:
            raise PQDriverLogicError("Laser port not open.") 
            return 0

    def get_frequency_mode(self):
        """
        Poll the Sepia driver for the currently set frequency mode: 0 (80MHz), 1 (40MHz), 2 (20MHz), 3 (10MHz), 4 (5MHz), 5 (2.5MHz), 6 (external pulse, rising edge), 7 (external pulse, falling edge)

        :returns: frequency_mode
        :rtype:
        """
        if self.isConnected:
            mode = decode_freq_trig_mode(self.get_pulse_params()[0])
            SMELLIELogger.debug('SNODROP DEBUG: PQDriver.get_frequency_mode() = {}'.format(mode))
            return mode
        else:
            raise PQDriverLogicError("Laser port not open.") 
            return 0

    def get_pulse_mode(self):
        """
        Poll the Sepia driver for the currently set pulse mode: 0 (continuous), 1 (pulsed)

        :returns: pulse_mode
        :rtype: int
        """
        if self.isConnected:
            pulse_mode = bool(self.get_pulse_params()[1])
            SMELLIELogger.debug('SNODROP DEBUG: PQDriver.get_pulse_mode() = {}'.format(pulse_mode))
            return pulse_mode
        else:
            raise PQDriverLogicError("Laser port not open.") 
            return 0

    def get_head_type(self):
        """
        Poll the Sepia driver for the currently set head type

        :returns: head_type
        :rtype: int
        """
        if self.isConnected:
            head_type = self.get_pulse_params()[2]
            SMELLIELogger.debug('SNODROP DEBUG: PQDriver.get_head_type() = {}'.format(head_type))
            return head_type
        else:
            raise PQDriverLogicError("Laser port not open.") 
            return 0
        
    def check_pulse_mode(self):
        """
        Check which pulse mode is set in the Sepia driver - it must *always* be used in *pulsed* mode (1), and never in continuous mode (0)

        :raises: :class:`.PQDriverHWError` if pulsed mode is not set
        """
        if self.isConnected:
            SMELLIELogger.debug('SNODROP DEBUG: PQDriver.check_pulse_mode()')
            if not self.get_pulse_params()[1] == 1:
                raise PQDriverHWError("Laser Driver is not in pulsed mode!!")
        else:
            raise PQDriverLogicError("Laser port not open.") 

    def check_trig_mode(self):
        """
        Check which trigger mode is set in the Sepia driver

        :raises: :class:`.PQDriverHWError` if pulsed mode is not set
        """
        if self.isConnected:
            SMELLIELogger.debug('SNODROP DEBUG: PQDriver.check_trig_mode()')
            if not self.get_pulse_params()[0] == 6:
                raise PQDriverHWError("Laser Driver is not in external trigger (rising edge) mode!")
        else:
            raise PQDriverLogicError("Laser port not open.") 

    def get_intensity(self):
        """
        Poll the Sepia driver for the currently set laser head intensity: a percentage between 0 and 100, in increments of 0.1%

        :returns: intensity
        :rtype: int
        """
        if self.isConnected:
            intensity = get_intensity_fine_step(self.dev_id, self.laser_slot_id)
            SMELLIELogger.debug('SNODROP DEBUG: PQDriver.get_intensity() = {}'.format(intensity))
            return intensity
        else:
            raise PQDriverLogicError("Laser port not open.") 
            return 0

    def set_intensity(self, intensity):
        """
        Set the laser head intensity: a percentage between 0 and 100, in increments of 0.1%

        :param intensity: requested laser head intensity
        :type intensity: double

        :raises: :class:`.PQDriverHWError` if the command is unsuccessful
        """
        if self.isConnected:
            SMELLIELogger.debug('SNODROP DEBUG: PQDriver.set_intensity({})'.format(intensity))
            set_intensity_fine_step(self.dev_id, self.laser_slot_id, intensity)
            if not self.get_intensity() == intensity:
                raise PQDriverHWError("Cannot set Laser head intensity!")
        else:
            raise PQDriverLogicError("Laser port not open.") 

    def is_laser_locked(self):
        """
        Poll the Sepia driver for the lock status.
        
        :returns: True if the power is off, the soft-lock is on or the sepia key is locked
        """
        if self.isConnected:
            locked_status = get_laser_locked(self.dev_id, self.driver_slot_id)
            SMELLIELogger.debug('SNODROP DEBUG: PQDriver.is_laser_locked() = {}'.format(locked_status))
            return locked_status
        else:
            raise PQDriverLogicError("Laser port not open.") 
            return 0

    def is_soft_lock_on(self):
        """
        Poll the Sepia driver for the status of the soft-lock
        
        :returns: True if the soft lock is on
        """
        if self.isConnected:
            locked_status = get_laser_soft_lock(self.dev_id, self.driver_slot_id)
            SMELLIELogger.debug('SNODROP DEBUG: PQDriver.is_soft_lock_on() = {}'.format(locked_status))
            return locked_status
        else:
            raise PQDriverLogicError("Laser port not open.") 
            return 0

    def set_soft_lock(self, is_locked = True):
        """
        Set the PQ driver soft-lock to on
        """
        if self.isConnected:
            SMELLIELogger.debug('SNODROP DEBUG: PQDriver.set_soft_lock({})'.format(is_locked))
            if is_locked != self.is_soft_lock_on():
                set_laser_soft_lock(self.dev_id, self.driver_slot_id, is_locked)
        else:
            raise PQDriverLogicError("Laser port not open.") 

    def go_safe(self):
        """
        Set PQ driver into its safe state: soft-lock = on, intensity = 0%
        """
        if self.isConnected:
            SMELLIELogger.debug('SNODROP DEBUG: PQDriver.go_safe()')
            self.set_soft_lock(is_locked = True)
            self.set_intensity(0)
            set_pulse_parameters(self.dev_id, self.laser_slot_id)
        else:
            raise PQDriverLogicError("Laser port not open.") 

    def go_ready(self, intensity):
        """
        Set PQ driver into its ready state, given intensity, sets soft-lock = off
        """
        if self.isConnected:
            SMELLIELogger.debug('SNODROP DEBUG: PQDriver.go_ready()')
            self.set_intensity(intensity)
            self.set_soft_lock(False)
        else:
            raise PQDriverLogicError("Laser port not open.") 
        
    def get_firmware_version(self):
        """
        Get the current PQ driver firmware version as a string
        """
        if self.isConnected:
            fwr_ver = get_fwr_version(self.dev_id)
            SMELLIELogger.debug('SNODROP DEBUG: PQDriver.get_firmware_version() = {}'.format(fwr_ver))
            return fwr_ver
        else:
            raise PQDriverLogicError("Laser port not open.") 
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
            checkValue = self.is_soft_lock_on() #choose to check the softlock:
            if (checkValue == True or checkValue == False): isAlive = True
            else: isAlive = False
            return isAlive
        else:
            raise PQDriverLogicError("Laser port not open.") 
            return 0 

    def system_state(self):
        """
        Returns a formatted string with the hardware info and constant settings.
        """
        if self.isConnected:
            return "PQ laser (system):: Firmware Version : {}, Pulse Mode : {}, Pulse Parameters : ({})".format(self.get_firmware_version(),self.get_pulse_mode(), ", ".join(str(x) for x in self.get_pulse_params()), self.get_frequency_mode())
        else:
            raise PQDriverLogicError("Laser port not open.") 
            return 0

    def current_state(self):
        """
        Returns a formatted string with the current hardware settings
        """
        if self.isConnected:
            return "PQ laser (settings):: Laser Locked : {}, Soft Lock : {}, Intensity : {}/1000, Frequency Mode : {}".format("Locked" if self.is_laser_locked() else "Unlocked", 
               "On " if self.is_soft_lock_on() else "Off", 
               self.get_intensity(), self.get_frequency_mode())
        else:
            raise PQDriverLogicError("Laser port not open.") 
            return 0
