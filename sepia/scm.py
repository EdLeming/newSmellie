from sepia import dll, raise_on_error_code
from ctypes import c_ubyte, byref,c_int32

"""
Device Operational Safety Controller Functions (SCM)
From the original C-API: `This module implements the safety features of the PQ Laser Device, as there are the thermal and voltage monitoring, the interlock (hard locking) and soft locking capabilities`.
"""

@raise_on_error_code
def get_laser_soft_lock(dev_id, slot_id):
    """
    Return the contents of the soft-lock register.
    Remember: a hard-lock overrides a soft-lock, so this isn't necessarily the same as the state of the laser.

    :param dev_id: the SEPIA device number, ordered from 0
    :type dev_id: int

    :param slot_id: the slot number, between 000 and 989
    :type slot_id: int

    :returns: is_locked
    :type is_locked: bool
    """
    contents = c_ubyte()
    dll.SEPIA2_SCM_GetLaserSoftLock( dev_id, slot_id, byref(contents) )
    return bool(contents.value)

@raise_on_error_code
def set_laser_soft_lock(dev_id, slot_id, contents):
    """
    Set the contents of the soft-lock register.
    Remember: a hard-lock overrides a soft-lock, so this isn't necessarily the same as the state of the laser.
    
    :param dev_id: the SEPIA device number, ordered from 0
    :type dev_id: int

    :param slot_id: the slot number, between 000 and 989
    :type slot_id: int

    :param contents: the soft-lock register
    :type contents: bool
    """    
    dll.SEPIA2_SCM_SetLaserSoftLock(dev_id, slot_id, c_ubyte(contents))

@raise_on_error_code
def get_laser_locked(dev_id, slot_id):
    """
    Get the state of the laser power-line
    This will return 'True' if the power is off, if the soft-lock is on, if the hard-lock (key on SEPIA) is on or the SMELLIE interlock is OPEN (otherwise will be 'False') i.e. True = Locked & False = Unlocked.

    :param dev_id: the SEPIA device number, ordered from 0
    :type dev_id: int

    :param slot_id: the slot number, between 000 and 989
    :type slot_id: int

    :returns: power_state
    :type power_state: bool    
    """
    state = c_ubyte()
    dll.SEPIA2_SCM_GetLaserLocked(dev_id, slot_id, byref(state) )
    return bool(state.value)
