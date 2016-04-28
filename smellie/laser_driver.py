from sepia.usb import close_usb_device, open_usb_device
from sepia.fwr import free_module_map, get_module_map, get_fwr_version
from sepia.slm import set_intensity_fine_step, get_pulse_parameters, set_pulse_parameters
from sepia.com import get_module_type, decode_module_type
from config import LASER_DRIVER_DEV_ID, LASER_DRIVER_SLOT_ID

"""
Control of the SEPIA II Laser Driver hardware
"""

class LaserDriverLogicError(Exception):
    """
    Thrown if an inconsistency is noticed *before* any instructions are sent to the hardware (i.e. a problem with code logic)
    """
    pass

class LaserDriverHWError(Exception):
    """
    Thrown if an inconsistency is noticed *after* any hardware instruction is executed (i.e. a problem with the hardware itself)
    """
    pass

class LaserDriver(object):
    """
    Controls the Laser Driver via commands sent down a USB port.
    """
    def __init__(self):
        self.dev_id  = LASER_DRIVER_DEV_ID
        self.slot_id = LASER_DRIVER_SLOT_ID
    
    def open_connection(self):
        """
        Open the USB connection to SEPIA
        """
        open_usb_device(self.dev_id)
        get_module_map(self.dev_id)
        
    def close_connection(self):
        """
        (Cleanly!) close the USB connection to SEPIA
        """
        free_module_map(self.dev_id)
        close_device(self.dev_id)

    def get_pulse_params(self):
        """
        Poll SEPIA for a summary of the current device parameters: frequency mode, pulse mode and head type

        :returns: parameters
        :type parameters: string
        """
        return get_pulse_parameters(self.dev_id, self.slot_id)

    def set_frequency_mode(self, frequency_mode):
        """
        Set the SEPIA frequency mode: 0 (80MHz), 1 (40MHz), 2 (20MHz), 3 (10MHz), 4 (5MHz), 5 (2.5MHz), 6 (external pulse, rising edge), 7 (external pulse, falling edge)

        :param frequency_mode: requested frequency mode
        :type frequency_mode: int
        """
        set_pulse_params(self.dev_id, self.slot_id, freqency_mode)

    def get_frequency_mode(self):
        """
        Poll SEPIA for the currently set frequency mode: 0 (80MHz), 1 (40MHz), 2 (20MHz), 3 (10MHz), 4 (5MHz), 5 (2.5MHz), 6 (external pulse, rising edge), 7 (external pulse, falling edge)

        :returns: frequency_mode
        :type frequency_mode: int
        """
        return self.get_pulse_params()[0]

    def get_pulse_mode(self):
        """
        Poll SEPIA for the currently set pulse mode: 0 (continuous), 1 (pulsed)

        :returns: pulse_mode
        :type pulse_mode: int
        """
        return self.get_pulse_params()[1]

    def get_head_type(self):
        """
        Poll SEPIA for the currently set head type

        :returns: head_type
        :type head_type: int
        """
        return self.get_pulse_params()[2]
        
    def check_pulse_mode(self):
        """
        Check which pulse mode is set in SEPIA - it must *always* be used in *pulsed* mode (1), and never in continuous mode (0)

        :raises: :class:`.LaserDriverHWError` if pulsed mode is not set
        """
        if not self.get_pulse_parameters()[1] == 1:
            raise LaserDriverHWError("Laser Driver is not in pulsed mode!!")

    def get_intensity(self):
        """
        Poll SEPIA for the currently set laser head intensity: a percentage between 0 and 100, in increments of 0.1%

        :returns: intensity
        :type intensity: double
        """
        return get_intensity_fine_step(self.dev_id, self.slot_id, intensity)

    def set_intensity(self, intensity):
        """
        Set the laser head intensity: a percentage between 0 and 100, in increments of 0.1%

        :param intensity: requested laser head intensity
        :type intensity: double

        :raises: :class:`.LaserDriverHWError` if the command is unsuccessful
        """
        set_intensity_fine_step(self.dev_id, self.slot_id, intensity)
        if not self.get_intensity() == intensity:
            raise LaserDriverHWError("Cannot set Laser head intensity!")

    def is_soft_lock_on(self):
        """
        Poll SEPIA for the status of the soft-lock
        """
        return get_laser_soft_lock(self.dev_id, self.slot_id)

    def set_soft_lock(self, is_locked = True):
        """
        Set the SEPIA soft-lock to on
        """
        set_laser_soft_lock(self.dev_id, self.slot_id, is_locked)

    def go_safe(self):
        """
        Set SEPIA into its safe state: soft-lock = on, frequency mode = 6 (external, rising edge), intensity = 0%
        """
        self.set_soft_lock(is_locked = True)
        self.set_frequency_mode(6)
        self.set_intensity(0)

    def get_firmware_version(self):
        """
        Get the current SEPIA firmware version as a string
        """
        return get_fwr_version(self.dev_id)

    def current_state(self):
        """
        Returns a formatted string with the current hardware settings
        """
        return """Soft Lock : {0}
Intensity : {1}/1000
Pulse Mode : {2}
Pulse Parameters : {3}
Frequency Mode : {4}
Firmware Version : {5}
""".format("On " if self.get_laser_soft_lock() else "Off", 
           self.get_intensity(), 
           self.get_pulse_mode(), 
           ", ".join(srt(x) for x in self.get_pulse_params()),
           self.get_frequency_mode(), 
           self.get_firmware_version())
