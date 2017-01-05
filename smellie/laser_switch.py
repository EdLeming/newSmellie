from smellie_config import RELAY_COM_CHANNEL, RELAY_SLEEP, RESET_NAME
from time import sleep
import u12, subprocess 
from smellie.smellie_logger import SMELLIELogger

"""
Control of the Laser Switch hardware
"""

def invert(bit):
    """
    Invert the input bit, i.e. convert 0 to 1, or 1 to 0

    :param bit: the input bit
    """
    if bit in (0, 1):
        return int(not bit)
    raise TypeError("Cannot invert bit - not a boolean!")

def translate_bits(b0, b1, b2):
    """
    Convert a binary bit string into an integer, according to big-endian ordering
    
    :param b0: bit 0
    :param b1: bit 1    
    :param b2: bit 2
    """
    return int("{2}{1}{0}".format(b0, b1, b2), 2)

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
    Controls the Laser Switch via commands sent down a USB port.
    The port number is set in config.py .
    """
    def __init__(self):
        self.com_channel = RELAY_COM_CHANNEL
        self.connection = u12.U12()
    
    def selected_channel_up(self):
        """
        Increment the currently selected Laser Switch channel by + 1

        :raises: :class:`.LaserSwitchHWError` if the command is unsuccessful
        """
        SMELLIELogger.debug('SNODROP DEBUG: LaserSwitch.selected_channel_up()')
        channel_original = self.get_selected_channel()
        self.connection.eDigitalOut(self.com_channel, 1, writeD = 1) 
        self.connection.eDigitalOut(self.com_channel, 0, writeD = 1)
        self.connection.eDigitalOut(self.com_channel, 1, writeD = 1)
        
        channel_new = self.get_selected_channel()
        if (channel_original<5) and (1 + channel_original) != channel_new:
            raise LaserSwitchHWError("Failed to increment the selected Laser Switch channel number!")
        elif (channel_original==5) and channel_new!=0: ## chan 5 -> 0
            raise LaserSwitchHWError("Failed to increment the selected Laser Switch channel number!")

    def execute(self):
        """
        Change the active Laser Switch channel from the currently active one to the currently selected one
        """
        SMELLIELogger.debug('SNODROP DEBUG: LaserSwitch.execute()')
        self.connection.eDigitalOut(0, 1, writeD = 1) 
        self.connection.eDigitalOut(0, 0, writeD = 1)      
        self.connection.eDigitalOut(0, 1, writeD = 1)

        sleep(RELAY_SLEEP)
        #self.force_USB_restart() #should not have to do this now!. Beware of other devices same hub
        #sleep(RELAY_SLEEP)
        
    def get_selected_channel(self):
        """
        Poll the Laser Switch for the current selected channel, i.e. the one which will become "active" with the next "execute" command

        :returns: selected channel
        :type selected channel: int
        """
        bit1 = invert(self.connection.eDigitalIn(2, readD = 1)["state"])
        bit2 = invert(self.connection.eDigitalIn(3, readD = 1)["state"])
        bit3 = invert(self.connection.eDigitalIn(4, readD = 1)["state"])
        
        channel = translate_bits(bit1,bit2,bit3)
        SMELLIELogger.debug('SNODROP DEBUG: LaserSwitch.get_selected_channel() = {}'.format(channel))
        return channel
        
    def get_active_channel(self):
        """
        Poll the Laser Switch for the current active channel, i.e. corresponding to the currently operating laser head

        :returns: active channel
        :type active channel: int

        :raises: :class:`.LaserSwitchHWError` if the command is unsuccessful
        """
        bit1 = invert(self.connection.eDigitalIn(5, readD = 1)["state"])
        bit2 = invert(self.connection.eDigitalIn(6, readD = 1)["state"])
        bit3 = invert(self.connection.eDigitalIn(7, readD = 1)["state"])
        
        channel = translate_bits(bit1,bit2,bit3)
        if not channel in xrange(6):
            raise LaserSwitchHWError("Laser Switch returned unphysical active channel number!  It should be between 0 and 5 inclusive.")
        SMELLIELogger.debug('SNODROP DEBUG: LaserSwitch.get_active_channel() = {}'.format(int(channel)))
        return int(channel)

    # Return the currently active channel as shown on the Laser Switch front panel's LEDs
    # Function from old code, still here for testing purposes.
    def GetActiveChannel(self):
        def invert(bit):
            if (bit == 0):
                bit = 1
                return bit
            elif(bit == 1):
                bit = 0
                return bit 
            else:
                return "Laser Switch (Get Active Channel) - Invalid input ... check connections to and from the Laser Switch."
                
        channel = invert(self.connection.eDigitalIn(5, readD = 1)["state"]) + (2.0 * float(invert(self.connection.eDigitalIn(6, readD = 1)["state"]))) + (4.0 * float(invert(self.connection.eDigitalIn(7, readD = 1)["state"])))
        SMELLIELogger.debug('SNODROP DEBUG: LaserSwitch.GetActiveChannel() = {}'.format(int(channel)))
        return int(channel)
        
    def set_active_channel(self, channel):
        """
        Set the active Laser Switch channel - must be between 0 and 5 inclusive
        
        :param channel: requested active channel

        :raises: :class:`.LaserSwitchLogicError` if the requested active channel number is unphysical
        """
        SMELLIELogger.debug('SNODROP DEBUG: LaserSwitch.set_active_channel({})'.format(int(channel)))
        if (self.get_active_channel() != channel):
            if not channel in xrange(6):
                raise LaserSwitchLogicError("Cannot set selected Laser Switch channel to {0} - must be between 0 and 5 inclusive.".format(channel))
            while(channel != self.get_selected_channel()):
                self.selected_channel_up()
            self.execute()
        
    def force_USB_restart(self):
        """
        Resets the USB internal hub (to resolve USB errors). Should no longer need this! This was only to reset the sepia controller when it had problems being disconnected by the laser switch (when reconnecting to USB).
        
        :returns: successful reset (True) or otherwise (False) (boolean)
        """
        SMELLIELogger.debug('SNODROP DEBUG: LaserSwitch.force_USB_restart()')
        path = r"C:\Program Files (x86)\Windows Kits\10\Tools\x64\devcon.exe"
        try:
            response = subprocess.check_output([path,"restart",RESET_NAME]) 
            print "response1:",response
        except subprocess.CalledProcessError as e:
            response = e.output
            print "responseExc",response
            
        if (response[-24:-2]=="1 device(s) restarted."): return True
        else: raise LaserSwitchHWError("Failed to reset the USB hub : ".format(response))
        
    def is_connected(self):
        """   
        Check if the connection to the device is open
        For the laser switch, this just calls is_alive()
        """
        return self.is_alive()
        
    def is_alive(self):
        """
        Quick check alive or not.
        """
        isAlive = None
        checkValue = self.get_active_channel() #choose to check current active laser 
        if (checkValue==1 or checkValue==2 or checkValue==3 or checkValue==4 or checkValue==5 ): isAlive = True
        else: isAlive = False
        return isAlive
            
    def system_state(self):
        """
        Returns a formatted string with the hardware info and constant settings.
        
        :returns: Selected channel : {1}
        """
        return "Laser switch (system):: Selected channel : {}".format( self.get_selected_channel() )

    def current_state(self):
        """
        Return a formatted string with the current hardware settings
        
        :returns:Active channel : {0}
        """
        return "Laser switch (settings):: Active channel : {}".format( self.get_active_channel() )
