from smellie_config import VARIANDFILTER_SERIAL_PORT, VARIANDFILTER_BAUD_RATE, VARIANDFILTER_WAIT_TIME
from serial import Serial
from time import sleep

"""
Control of the Varia stepper motor arduino controller hardware
"""

class VariaNDFilterLogicError(Exception):
    """
    Thrown if an inconsistency is noticed *before* any instructions are sent to the hardware (i.e. a problem with code logic)
    """
    pass

class VariaNDFilterHWError(Exception):
    """
    Thrown if an inconsistency is noticed *after* any hardware instruction is executed (i.e. a problem with the hardware itself)
    """
    pass
   
class VariaNDFilter(object):

    def __init__(self):
        """
        Controls the arduino stepper motor controller attached to the Varia ND filter.
        """
        self.serial = None
        self.acceleration = 1
        self.isConnected = False
         
    def port_open(self):
        """
        Send a command message over the serial port for the motor controller to execute.  The message is automatically followed by \\r\\n , so you do not need to add this.

        :param msg:
        :type msg: string
        """
        if not self.isConnected:
            self.channel_num = None
            self.serial = Serial(VARIANDFILTER_SERIAL_PORT,VARIANDFILTER_BAUD_RATE,timeout=1)
            sleep(2)
            self.serial.flushInput()
            self.serial.flushOutput()
            sleep(VARIANDFILTER_WAIT_TIME)
            self.isConnected = True
        else:
            raise VariaNDFilterLogicError("Varia NDFilter port already open.") 
            
    def port_close(self):
        """
        Send a command message over the serial port for the motoro controller to execute.  The message is automatically followed by \\r\\n , so you do not need to add this.

        :param msg:
        :type msg: string
        """
        if self.isConnected: 
            self.serial.close()
            self.isConnected = False
        else:
            raise VariaNDFilterLogicError("Varia NDFilter port not open.")
                    
    def execute_message(self, msg):
        """
        Send a command message over the serial port for the motoro controller to execute.  The message is automatically followed by \\r\\n , so you do not need to add this.

        :param msg:
        :type msg: string
        """
        if self.isConnected:
            self.serial.write(msg+"\r\n")
            sleep(VARIANDFILTER_WAIT_TIME)
        else:
            raise VariaNDFilterLogicError("Varia NDFilter port not open.")
       
    def read_back(self):
        """
        Wait for a configuration-determined time, and read back a line from the hardware

        :returns: message
        :type message: string
        """
        if self.isConnected:
            readback = self.serial.readline()
            sleep(VARIANDFILTER_WAIT_TIME)
            return readback
        else:
            raise VariaNDFilterLogicError("Varia NDFilter port not open.")
            return 0
     
    def get_connected_status(self):
        """
        Send a command to query the status of the Varia stepper motor arduino controller
        :param msg:
        :returns: get the current connection status of the controller. If connected returns: 'Connected.' (string)
        """
        self.execute_message( "z" )
        return str(self.read_back()).replace('\r\n','')

    def get_position(self):
        """
        Send a command to query the status of the Varia stepper motor arduino controller
        :param msg:
        :returns: get the current position of the motor 'Position: {}' (string)
        """
        self.execute_message( "a" )
        return str(self.read_back()).replace('\r\n','')

    def get_max_speed(self):
        """
        Send a command to query the status of the Varia stepper motor arduino controller
        :param msg:
        :returns: max speed of motor 'Max Speed: {}' (string)
        """
        self.execute_message( "j" )
        return str(self.read_back()).replace('\r\n','')

    def set_max_speed(self, speedValue=5):
        """
        Send a command to the Varia stepper motor arduino controller
        The default argument is 5, which sets the acceleration to 5 step/s.
        
        :param msg: 'c'
        :type msg: string
        """
        self.execute_message( "c"+str(speedValue) )

    def set_acceleration(self, accelValue=1):
        """
        Send a command to the Varia stepper motor arduino controller
        The default argument is 1, which sets the acceleration to 1 step/s/s.
        
        :param msg: 'i'
        :type msg: string
        """
        self.execute_message( "i"+str(accelValue) )
        self.acceleration = accelValue
        
    def set_position(self, positionValue=0):
        """
        Send a command to the Varia stepper motor arduino controller
        The default argument is 0, which sets the position to the current position.

        :param msg: 'd'
        :type msg: string
        """
        self.execute_message( "d"+str(positionValue) )
        
    def set_reference_position(self, positionValue=0):
        """
        Send a command to the Varia stepper motor arduino controller
        The default argument is 0, which sets the reference position to the current position.
        
        :param msg: 'e'
        :type msg: string
        """
        self.execute_message( "e"+str(positionValue) )
        
    def get_home_status(self):
        """
        Send a command to query the status of the Varia stepper motor arduino controller. 
        The sensor is read by a digital pin and is high (1) when the switch is not pressed (low when pressed i.e. at home).
        Controller returns either 'Home sensor: 0' or 'Home sensor: 1' which is converted to True/False.
        :param msg:
        :returns: status of home switch: True, False or None (for a return string which isn't recognised) (string)
        """
        self.execute_message( "f" )
        response = str(self.read_back()).replace('\r\n','')
        if (response == 'Home sensor: 1'):
            homeStatus = False
        elif (response == 'Home sensor: 0'):
            homeStatus = True
        else: homeStatus = None
        return homeStatus

    def is_connected(self):
        """   
        Check if the connection to the device is open
        """
        return self.isConnected
        
    def is_alive(self):
        """
        Quick check alive or not.
        """
        checkValue = self.get_home_status() #choose to check the home status
        if (checkValue == True or checkValue == False): isAlive = True
        else: isAlive = False
        return isAlive
        
    def system_state(self):
        """
        Returns a formatted string with the hardware info
        
        :returns: 'varia motor (system):: Port: COM{}, Baudrate: {}, Timeout: {}sec, Max Speed: {}, Acceleration: {}'
        """
        return "varia NDFilter (system):: Port: COM{}, Baudrate: {}, Timeout: {}sec, Max Speed: {}, Acceleration: {}".format( self.serial.port+1, self.serial.baudrate, self.serial.timeout, self.get_max_speed(), self.acceleration )
        
    def current_state(self):
        """
        Return a formatted string with the current hardware settings

        :returns: 'varia motor (settings):: Position: {}'
        """
        return "varia NDFilter (settings):: Position: {}".format( self.get_position() )


