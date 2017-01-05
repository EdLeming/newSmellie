from sepia import string_buffer, dll, raise_on_error_code, SepiaLogicError
from ctypes import c_int32, c_ubyte, byref, c_ushort

"""
Laser Driver Functions (SLM)
From the original C-API: `SLM 828 modules can interface the huge families of pulsed laser diode heads (LDH series) and pulsed LED heads (PLS series) from PicoQuant. These functions let the application control their working modes and intensity`.
"""

@raise_on_error_code
def get_pulse_parameters(dev_id, slot_id):
    """
    Get the pulse parameters for the SLM module

    :param dev_id: the SEPIA device number, ordered from 0
    :type dev_id: int

    :param slot_id: the slot number, between 000 and 989
    :type slot_id: int

    :returns: freq the frequency mode of the module
    :type freq: int

    :returns: pulse_mode the pulse mode (1 = pulsed, or 0 = continuous [permanently disabled])
    :type pulse_mode: bool

    :returns: head_type
    :type head_type: int
    """
    freq = c_int32()
    pulse_mode = c_ubyte()
    head_type = c_int32()
    dll.SEPIA2_SLM_GetPulseParameters(dev_id, slot_id, byref(freq), byref(pulse_mode), byref(head_type) )
    return freq.value, pulse_mode.value, head_type.value

@raise_on_error_code
def set_pulse_parameters(dev_id, slot_id, freq_mode='EXT'):
    """
    Set the pulse parameters for the SLM module
    The original C-API has a parameter `bPulseMode` = 1 for pulsing, 0 for continuous light).  Using 0 can cause damage to the laser heads and so bPulseMode is hard coded to 1.    
    The `frequency mode` must be = 6 (triggering from the rising edge of the external trigger signal). The internal SEPIA triggers are MHz rate, and will damage the detector.

    :param dev_id: the SEPIA device number, ordered from 0
    :type dev_id: int

    :param slot_id: the slot number, between 000 and 989
    :type slot_id: int
    """
    #dev_id = dev_id[0]
    #slot_id = slot_id[""]
    
    # The last two parameters are the pulse and frequency modes - DO NOT CHANGE  (see above and __init__.py)!
    #dll.SEPIA2_SLM_SetPulseParameters(dev_id, slot_id, c_int32(6), c_ubyte(1))
    freq_mode_number = 6
    if freq_mode == 'INT': freq_mode_number = 5
        
    if (freq_mode_number!=6 or freq_mode_number!=5):
        dll.SEPIA2_SLM_SetPulseParameters(dev_id, slot_id, freq_mode_number, c_ubyte(1))
    else:
        raise SepiaLogicError("Freq mode must either be 'EXT' (default) or 'INT' (rising edge external trigger or internally generated 2.5MHz trigger.)")
    

@raise_on_error_code
def decode_freq_trig_mode(freq_mode):
    """
    Translate the frequency mode to a string for any SLM module

    :param freq_mode: the frequency mode - 0 (80MHz), 1 (40MHz), 2 (20MHz), 3 (10MHz), 4 (5MHz), 5 (2.5MHz), 6 (external pulse, rising edge), 7 (external pulse, falling edge)
    :type freq_mode: int

    :returns: mode_string
    :type mode_string: string

    :raises: :class:`.SepiaLogicError` if the frequency mode is invalid, i.e. not between 0 and 7
    """
    if not freq_mode in xrange(8):
        raise SepiaLogicError("Cannot decode the frequency mode - must be an integer between 0 and 7 inclusive")
    return_string = string_buffer()
    dll.SEPIA2_SLM_DecodeFreqTrigMode(freq_mode, return_string )
    return return_string.value

@raise_on_error_code
def get_intensity_fine_step(dev_id, slot_id):
    """
    Get the current intensity value of a given SLM driver module - an integer between 0 and 1000, where 1000 corresponds to 100% of the laser head's maximum control voltage (i.e. each integer increment represents 0.1% of the voltage)

    :param dev_id: the SEPIA device number, ordered from 0
    :type dev_id: int

    :param slot_id: the slot number, between 000 and 989
    :type slot_id: int

    :returns: intensity
    :type intensity: int
    """
    intensity = c_ushort()
    dll.SEPIA2_SLM_GetIntensityFineStep(dev_id, slot_id, byref(intensity) )
    return intensity.value

@raise_on_error_code
def set_intensity_fine_step(dev_id, slot_id, intensity):
    """
    Set the intensity value of a given SLM driver module - an integer between 0 and 1000, where 1000 corresponds to 100% of the laser head's maximum control voltage (i.e. each integer increment represents 0.1% of the voltage)

    :param dev_id: the SEPIA device number, ordered from 0
    :type dev_id: int

    :param slot_id: the slot number, between 000 and 989
    :type slot_id: int

    :param intensity: the requested laser head intensity
    :type intensity: int
    """
    if not intensity in xrange(int(1e3+1)):
        raise SepiaLogicError("Cannot set the intensity fine step - must be an integer between 0 and 1000")
    dll.SEPIA2_SLM_SetIntensityFineStep(dev_id, slot_id, intensity)

@raise_on_error_code
def decode_head_type(head_type_code):
    """
    Returns the head_type string at list position `head_type_code` for a given SLM module

    :param head_type_code: must be between 0 and 3 inclusive
    :type head_type_code: int

    :returns: head_type
    :type head_type: string

    :raises: :class:`.SepiaLogicError` if the head_type_code is invalid, i.e. not between 0 and 3	
    """
    if not head_type_code in xrange(4):
        raise SepiaLogicError("Cannot decode head type code - must be between 0 and 3")
    return_string = string_buffer()
    dll.SEPIA2_SLM_DecodeHeadType(head_type_code, return_string )
    return return_string.value
