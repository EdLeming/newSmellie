from smellie_config import LASER_SWITCH_SERIAL_PORT, LASER_SWITCH_BAUD_RATE, LASER_SWITCH_WAIT_TIME
from serial import Serial
from time import sleep
#from smellie.smellie_logger import SMELLIELogger

"""
Control of the Laser Switch hardware
"""

class LaserSwitchLogicError(Exception):
    """
    Thrown if an inconsistency is noticed *before* any instructions are sent to the hardware (i.e. a problem with code logic)
    """
    pass

class LaserSwitchHWError(Exception):
    """
    Thrown if an inconsistency is noticed *after* any hardware instruction is executed (i.e. a problem with the hardware itself)
    """
    pass

class LaserSwitch(object):
    """
    Controls the Laser Switch via commands sent down a serial port.
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
        #SMELLIELogger.debug('SNODROP DEBUG: LaserSwitch.port_open()')
        if not self.isConnected:
            self.serial = Serial(LASER_SWITCH_SERIAL_PORT, LASER_SWITCH_BAUD_RATE, timeout=1)
            sleep(1)
            self.isConnected = True
            self.flush()
        else:
            raise LaserSwitchLogicError("Laser switch port already open.")
        
    def port_close(self):
        """
        Close the serial port connection
        """
        #SMELLIELogger.debug('SNODROP DEBUG: LaserSwitch.port_close()')
        if self.isConnected:
            self.serial.close()
            self.isConnected = False
        else:
            raise LaserSwitchLogicError("Laser Switch port not open.")

    def execute_message(self, msg):
        """
        Send a command message over the serial port for the Laser Switch to execute.

        :param msg:
        :type msg: string
        """
        #SMELLIELogger.debug('SNODROP DEBUG: LaserSwitch.execute_message({})'.format(msg))
        if self.isConnected:
            self.serial.write(msg) #dont follow with \r\n for this Arduino program
            sleep(LASER_SWITCH_WAIT_TIME)
        else:
            raise LaserSwitchLogicError("Laser Switch port not open.") 
        
    def read_back(self):
        """
        Wait for a configuration-determined time, and read back a line from the hardware

        :returns: message
        :type message: string
        """
        if self.isConnected:
            readback = self.serial.readline()
            sleep(LASER_SWITCH_WAIT_TIME)
            #SMELLIELogger.debug('SNODROP DEBUG: LaserSwitch.read_back = {}'.format(readback))
            return str(readback).replace('\r\n','')
        else:
            raise LaserSwitchLogicError("Laser Switch port not open.")
            return 0
            
    def flush(self):
        """
        Flushes serial input and output buffers (used to get ready for next command).
        """
        if self.isConnected:
            self.serial.flushInput()
            self.serial.flushOutput()
        else:
            raise LaserSwitchLogicError("Interlock port not open.") 

    def get_active_channel(self):
        """
        Poll the Laser Switch for the current active channel, i.e. corresponding to the currently operating laser head

        :returns: active channel
        :type active channel: int

        :raises: :class:`.LaserSwitchHWError` if the command is unsuccessful
        """
        self.execute_message("b")
        channel_num = int(filter(str.isdigit, self.read_back()))
        
        if not channel_num in xrange(6):
            raise LaserSwitchHWError("Laser Switch returned unphysical active channel number!  It should be between 0 and 5 inclusive.")
        #SMELLIELogger.debug('SNODROP DEBUG: LaserSwitch.get_active_channel() = {}'.format(int(channel_num)))
        return int(channel_num)

    def get_selected_channel(self):
        """
        Poll the Laser Switch for the current selected channel number

        :returns: current channel
        :type current channel: int
        """
        self.execute_message("c")
        channel_num =  int(filter(str.isdigit, self.read_back()))
        #SMELLIELogger.debug('SNODROP DEBUG: LaserSwitch.get_present_channel() = {}\n'.format(str(channel_num)))
        return channel_num
            
    def selected_channel_up(self):
        """
        Increment the currently selected Laser Switch channel by + 1

        :raises: :class:`.LaserSwitchHWError` if the command is unsuccessful
        """
        #SMELLIELogger.debug('SNODROP DEBUG: LaserSwitch.selected_channel_up()')
        channel_original = self.get_selected_channel()
        self.execute_message("d")
        response = self.read_back()
        if (response!="Channel Select. Sent."):
            raise LaserSwitchHWError("Unrecognised response after select command. Check system.")
        
        channel_new = self.get_selected_channel()
        if (channel_original<5) and (1 + channel_original) != channel_new:
            raise LaserSwitchHWError("Failed to increment the selected Laser Switch channel number!")
        elif (channel_original==5) and channel_new!=0: ## chan 5 -> 0
            raise LaserSwitchHWError("Failed to increment the selected Laser Switch channel number!")

    def execute(self):
        """
        Change the active Laser Switch channel from the currently active one to the currently selected one
        """
        #SMELLIELogger.debug('SNODROP DEBUG: LaserSwitch.send_select_command()\n')
        self.execute_message("e")
        response = self.read_back()
        if (response!="Execute. Sent."):
            raise LaserSwitchHWError("Unrecognised response after select command. Check system.")
  
    def set_active_channel(self, channel):
        """
        Set the active Laser Switch channel - must be between 0 and 5 inclusive
        
        :param channel: requested active channel

        :raises: :class:`.LaserSwitchLogicError` if the requested active channel number is unphysical
        """
        #SMELLIELogger.debug('SNODROP DEBUG: LaserSwitch.set_active_channel({})'.format(int(channel)))
        if (self.get_active_channel() != channel):
            if not channel in xrange(6):
                raise LaserSwitchLogicError("Cannot set selected Laser Switch channel to {0} - must be between 0 and 5 inclusive.".format(channel))
            while(channel != self.get_selected_channel()):
                self.selected_channel_up()
            self.execute()
            
    def get_fwr_version(self):
        """
        Get the current Laser Switch firmware version as a string
        """
        self.execute_message("x")
        fwr_ver = self.read_back()
        #SMELLIELogger.debug('SNODROP DEBUG: LaserSwitch.get_fwr_version = {}'.format(fwr_ver))
        return fwr_ver

    def get_info(self):
        """
        Get the current Laser Switch hardware model as a string
        """ 
        self.execute_message("y")
        type = self.read_back()
        #SMELLIELogger.debug('SNODROP DEBUG: LaserSwitch.get_info = {}'.format(type))
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
        self.execute_message("z")
        connected = self.read_back()
        if (connected=="Connected."):
            isAlive = True
        else: isAlive = False
        return isAlive
        
    def system_state(self):
        """
        Returns a formatted string with the hardware info
        """
        return "Laser switch (system):: Port: COM{}, Baudrate: {}, Timeout: {}sec, Info:{}, Firmware:{}".format( self.serial.port+1, self.serial.baudrate, self.serial.timeout, self.get_info(), self.get_fwr_version() )  
        
    def current_state(self):
        """
        Return a formatted string with the current hardware settings

        :returns: 'LaserSwitch:: Present channel:{}, Selected Channel:{}'
        """
        return "Laser switch (settings):: Present channel:{}, Selected Channel:{}".format( str(self.get_present_channel()), str(self.get_selected_channel()) )
