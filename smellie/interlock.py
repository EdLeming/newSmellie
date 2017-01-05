from smellie_config import INTERLOCK_SERIAL_PORT, INTERLOCK_BAUD_RATE, INTERLOCK_WAIT_TIME
from serial import Serial
from time import sleep
from smellie.smellie_logger import SMELLIELogger

"""
Control of the Interlock hardware
"""

class InterlockLogicError(Exception):
    """
    Thrown if an inconsistency is noticed *before* any instructions are sent to the hardware (i.e. a problem with code logic)
    """
    pass

class InterlockHWError(Exception):
    """
    Thrown if an inconsistency is noticed *after* any hardware instruction is executed (i.e. a problem with the hardware itself)
    """
    pass

class Interlock(object):
    """
    Controls the interlock via commands sent down a serial port.
    The port number and baud rate are set in config.py
    """
    def __init__(self):
        self.serial = None
        self.isConnected = False
        SMELLIELogger.new_logger("Interlock")
        
    def port_open(self):
        """
        Open the serial port connection
        """
        SMELLIELogger.debug('SNODROP DEBUG: Interlock.port_open()')
        if not self.isConnected:
            self.serial = Serial(INTERLOCK_SERIAL_PORT,INTERLOCK_BAUD_RATE,timeout=2)
            sleep(1)
            self.isConnected = True
            self.flush()
        else:
            raise InterlockLogicError("Interlock port already open.") 
    
    def port_close(self):
        """
        Close the serial port connection
        """
        SMELLIELogger.debug('SNODROP DEBUG: Interlock.port_close()')
        if self.isConnected:
            self.serial.close()
            self.isConnected = False
        else:
            raise InterlockLogicError("Interlock port not open.")

    def execute_message(self, msg):
        """
        Send a command message over the serial port for the Fibre Switch to execute.  The message is automatically followed by \\r\\n , so you do not need to add this.

        :param msg:
        :type msg: string
        """
        if not msg=='1': SMELLIELogger.debug('SNODROP DEBUG: Interlock.execute_message({})'.format(msg)) #dont log all the keepalive messages
        if self.isConnected:
            self.flush()
            self.serial.write(msg+"\r\n")
            sleep(INTERLOCK_WAIT_TIME)
        else:
            raise InterlockLogicError("Interlock port not open.") 
        
    def read_back(self):
        """
        Wait for a configuration-determined time, and read back a line from the hardware

        :returns: message
        :type message: string
        """
        if self.isConnected:
            readback = self.serial.readline()
            sleep(INTERLOCK_WAIT_TIME)
            SMELLIELogger.debug('SNODROP DEBUG: Interlock.read_back() = {}'.format(readback))
            return str(readback).replace('\r\n','')
        else:
            raise InterlockLogicError("Interlock port not open.")
            return 0
            
    def flush(self):
        """
        Flushes serial input and output buffers (used to get ready for next command).
        """
        if self.isConnected:
            self.serial.flushInput()
            self.serial.flushOutput()
        else:
            raise InterlockLogicError("Interlock port not open.")  

    def get_status(self):
        """
        Send a command to query the arm/disarm status of the internal relay
        :param msg:
        :returns: arm/disarm status message (string)
        """
        self.execute_message("v")
        response = self.read_back()
        if (response!='Relay contacts are CLOSED' and response!='Relay contacts are OPEN'):
            self.port_close()
            raise InterlockHWError("Unknown status response from interlock. Interlock state unknown.")
        SMELLIELogger.debug('SNODROP DEBUG: Interlock.get_status() = {}'.format(response))
        return response
        
    def lasers_are_locked(self):
        """
        Send a command to query the arm/disarm status of the internal relay
        :param msg:
        :returns: arm/disarm boolean: True for OPEN, False for CLOSED (None for unknown)
        i.e. disarmed = locked = relay contacts are open = True
        """
        status = None
        response = self.get_status()
        if (response=="Relay contacts are CLOSED"): status = False
        elif (response=="Relay contacts are OPEN"): status = True
        else: 
            raise InterlockHWError("Unknown status response from interlock. Interlock state unknown.")
        SMELLIELogger.debug('SNODROP DEBUG: Interlock.lasers_are_locked() = {}'.format(status))
        return status

    def set_arm(self):
        """
        Send a command to arm the interlock
        
        :param msg: 'a'
        :type msg: string
        :returns: arm message (string)
        """
        SMELLIELogger.debug('SNODROP DEBUG: Interlock.set_arm()')
        self.execute_message("a")
        arm_return = self.read_back()
        return arm_return
        
    def set_disarm(self):
        """
        Send a command to disarm the interlock

        :param msg: 'd'
        :type msg: string
        """
        SMELLIELogger.debug('SNODROP DEBUG: Interlock.set_disarm()')
        self.execute_message("d")
        response = self.read_back()
        return response
        
    def send_keepalive(self):
        """
        Send a command to the interlock to maintain its armed state
                
        :param msg: '1'
        :type msg: string
        """
        #SMELLIELogger.debug('SNODROP DEBUG: Interlock.send_keepalive()') #next level debugging
        self.execute_message("1")
        
    def is_connected(self):
        """   
        Check if the connection to the device is open
        """
        return self.isConnected
        
    def is_alive(self):
        """
        Quick check alive or not.
        """
        checkValue = self.lasers_are_locked()  #choose to check the interlock status:
        if (checkValue == True or checkValue == False): isAlive = True
        else: isAlive = False
        return isAlive
        
    def system_state(self):
        """
        Returns a formatted string with the hardware info and constant settings.

        :returns: 'Interlock (system):: Port:{}, Baudrate:{}, Status message:{}'
        """
        return "Interlock (system):: Port: COM{}, Baudrate: {}, Timeout: {}sec, Status: {}".format(self.serial.port+1, self.serial.baudrate, self.serial.timeout, self.get_status())

    def current_state(self):
        """
        Return a formatted string with the current hardware settings

        :returns: 'Interlock (settings):: Lasers Locked: {}'
        """
        return "Interlock (settings):: Lasers are locked: {}".format(self.lasers_are_locked())
 