from smellie_config import FIBRE_SWITCH_4CHAN_SERIAL_PORT, FIBRE_SWITCH_4CHAN_BAUD_RATE, FIBRE_SWITCH_4CHAN_WAIT_TIME
from serial import Serial
from time import sleep
from smellie.smellie_logger import SMELLIELogger

"""
Control of the Fibre Switch hardware
"""

class FibreSwitchLogicError(Exception):
    """
    Thrown if an inconsistency is noticed *before* any instructions are sent to the hardware (i.e. a problem with code logic)
    """
    pass

class FibreSwitchHWError(Exception):
    """
    Thrown if an inconsistency is noticed *after* any hardware instruction is executed (i.e. a problem with the hardware itself)
    """
    pass

def check_global_channel_number(channel_num):
    """
    Check the validity of the desired global Fibre Switch channel number, which must be at most 4

    :param channel_num: the global channel number to check

    :raises: :class:`.FibreSwitchLogicError` if the channel is unphysical, i.e. not between 1 and 4
    """
    if not (channel_num-1) in xrange(4):
        raise FibreSwitchLogicError("Invalid Fibre Switch channel {0} requested ... must be 1 - 4")

class FibreSwitch4Chan(object):
    """
    Controls the Fibre Switch via commands sent down a serial port.
    The port number and baud rate are set in config.py .
    """
    def __init__(self):
        self.channel_num = None
        self.serial = None
        self.isConnected = False

    def port_open(self):
        """
        Open the serial port connection
        """
        SMELLIELogger.debug('SNODROP DEBUG: FibreSwitch.port_open()')
        if not self.isConnected:
            self.serial = Serial(FIBRE_SWITCH_4CHAN_SERIAL_PORT, FIBRE_SWITCH_4CHAN_BAUD_RATE, timeout=1)
            sleep(1)
            self.isConnected = True
            self.flush()
        else:
            raise FibreSwitchLogicError("Fibre switch port already open.")
        
    def port_close(self):
        """
        Close the serial port connection
        """
        SMELLIELogger.debug('SNODROP DEBUG: FibreSwitch.port_close()')
        if self.isConnected:
            self.serial.close()
            self.isConnected = False
        else:
            raise FibreSwitchLogicError("Fibre Switch port not open.")

    def execute_message(self, msg):
        """
        Send a command message over the serial port for the Fibre Switch to execute.  The message is automatically followed by \\r\\n , so you do not need to add this.

        :param msg:
        :type msg: string
        """
        SMELLIELogger.debug('SNODROP DEBUG: FibreSwitch.execute_message({})'.format(msg))
        if self.isConnected:
            self.serial.write(msg+"\r\n")
            sleep(FIBRE_SWITCH_4CHAN_WAIT_TIME)
        else:
            raise FibreSwitchLogicError("Fibre Switch port not open.") 
        
    def read_back(self):
        """
        Wait for a configuration-determined time, and read back a line from the hardware

        :returns: message
        :type message: string
        """
        if self.isConnected:
            readback = self.serial.readline()
            sleep(FIBRE_SWITCH_4CHAN_WAIT_TIME)
            SMELLIELogger.debug('SNODROP DEBUG: FibreSwitch.read_back = {}'.format(readback))
            return readback
        else:
            raise FibreSwitchLogicError("Fibre Switch port not open.")
            return 0

    def flush(self):
        """
        Flushes serial input and output buffers (used to get ready for next command).
        """
        if self.isConnected:
            self.serial.flushInput()
            self.serial.flushOutput()
        else:
            raise FibreSwitchLogicError("Interlock port not open.")  
            
    def set_global_channel_number(self, channel_num):
        """
        Set the global Fibre Switch channel, and check that it succeeded

        :param channel_num: requested new global channel number

        :raises: :class:`.FibreSwitchLogicError`: if the requested global channel number is unphysical

        :raises: :class:`.FibreSwitchHWError` if the command is unsuccessful
        """ 
        SMELLIELogger.debug('SNODROP DEBUG: FibreSwitch.set_global_channel_number({})'.format(channel_num))
        check_global_channel_number(channel_num)
        self.execute_message("ch{0}".format(channel_num))
        if(self.get_global_channel_number() != channel_num): #check set value was set
            raise FibreSwitchHWError("Failed to set Fibre Switch to {0}".format(channel_num))
        else:
            self.channel_num = channel_num

    def get_global_channel_number(self):
        """
        Poll the Fibre Switch for the current global channel number

        :returns: current channel
        :type current channel: int
        """
        self.execute_message("ch?")
        channel_num = int(str(self.read_back()).replace('\n',' ').replace('\r','').replace(' ',''))
        SMELLIELogger.debug('SNODROP DEBUG: FibreSwitch.get_global_channel_number() = {}\n'.format(str(channel_num)))
        return channel_num

    def get_fwr_version(self):
        """
        Get the current Fibre Switch firmware version as a string
        """
        self.execute_message("firmware?")
        fwr_ver = str(self.read_back()).replace(' ','').replace('\r\n','')
        SMELLIELogger.debug('SNODROP DEBUG: FibreSwitch.get_fwr_version = {}'.format(fwr_ver))
        return fwr_ver

    def get_type(self):
        """
        Get the current Fibre Switch hardware model as a string
        """ 
        self.execute_message("type?")
        type = str(self.read_back()).replace(' ','').replace('\r\n','')
        SMELLIELogger.debug('SNODROP DEBUG: FibreSwitch.get_type = {}'.format(type))
        return type

    def is_connected(self):
        """   
        Check if the connection to the device is open
        """
        return self.isConnected

    def is_alive(self):
        """
        Quick check alive or not.
        """
        if (self.get_type() == 'mol5x14'): isAlive = True #choose to check the HW model:
        else: isAlive = False
        return isAlive
        
    def system_state(self):
        """
        Returns a formatted string with the hardware info
        """
        return "Fibre switch (system):: Port: COM{}, Baudrate: {}, Timeout: {}sec, Type:{}, Firmware:{}".format( self.serial.port+1, self.serial.baudrate, self.serial.timeout, self.get_type(), self.get_fwr_version() )  
        
    def current_state(self):
        """
        Return a formatted string with the current hardware settings

        :returns: 'FibreSwitch:: Port:{}, Baudrate:{}, Type:{}, Firmware version:{}, Channel:{}'
        """
        return "Fibre switch (settings):: Channel:{}".format( str(self.get_global_channel_number()) )
