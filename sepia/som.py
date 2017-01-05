from sepia import dll, raise_on_error_code
from ctypes import c_int32, create_string_buffer, byref

"""
Basic Oscillator Functions (SOM)
The following list represents the API of the basic oscillator module SOM 828.
"""

def string_buffer():
    """   
    :returns: ctype string buffer, the size of which is set in :mod:config
    """
    return create_string_buffer(100)

@raise_on_error_code
def get_freq_trig_mode(dev_id, slot_id):
    """
    Get the current frequency setting for the reference source of the given SOM

    :param dev_id: the SEPIA device number, ordered from 0
    :type dev_id: int

    :param slot_id: the slot number, between 000 and 989
    :type slot_id: int

    :returns: freq_trig_mode
    :type freq_trig_mode: int
    """
    mode = c_int32()
    dll.SEPIA2_SOM_GetFreqTrigMode(dev_id, slot_id, byref(mode))
    return mode.value
    
def decode_freq_trig_mode(dev_id, slot_id, mode):
    """
    Decode the frequency mode to a string

    :param dev_id: the SEPIA device number, ordered from 0
    :type dev_id: int

    :param slot_id: the slot number, between 000 and 989
    :type slot_id: int

    :returns: freq_trig_mode
    :type freq_trig_mode: char
    """
    mode_string = string_buffer()
    dll.SEPIA2_SOM_DecodeFreqTrigMode(dev_id, slot_id, mode, mode_string)
    return mode_string.value
    
