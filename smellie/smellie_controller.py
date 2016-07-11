from laser_driver import LaserDriver
from laser_switch import LaserSwitch
from fibre_switch import FibreSwitch
from ni_trigger_generator import TriggerGenerator
from ni_gain_control import GainVoltageGenerator
import system_state
<<<<<<< HEAD
import config
=======
from time import sleep
>>>>>>> e565c76c18b86af8f012ae960544c2865c619d46

class SmellieController(object):    
    def __enter__(self):
        """
        Open the SMELLIE Controller, with all hardware in deactivated mode
        """        
        self.fibre_switch = FibreSwitch()              
        self.laser_switch = LaserSwitch()              
        self.gain_voltage = GainVoltageGenerator()
        self.trig_signals = TriggerGenerator()
        self.laser_driver = LaserDriver()              
        self.laser_driver.open_connection()            
        self.deactivate()                              

    def __exit__(self, type, value, traceback):
        """
        Clean up code goes here - it is guaranteed to get called even if an exception is thrown during one of the other functions
        """
        self.deactivate()
        self.laser_driver.close_connection()

    def go_safe(self):
        """
        Send the entire SMELLIE system into `safe mode` - SEPIA soft-lock = on, SEPIA intensity = 0%
        """		
        self.laser_driver.go_safe()
        return 0

    def deactivate(self):
        """
        Send the entire SMELLIE system into `deactivated mode` - SEPIA soft-lock = on, SEPIA intensity = 0%, NI gain voltage = 0V, active Laser Switch channel = 0 (no laser head attached to this channel), Fibre Switch input channel = 5 and output channel = 14 (no detector fibre attached to this output channel)
        """
        self.go_safe()
        self.gain_voltage_gen.go_safe()
        self.laser_switch.set_active_channel(0)
        self.fibre_switch.set_io_channel_numbers(5, 14)
        return 0

    def laserheads_master_mode(self, ls_chan, intensity, fs_input_chan, fs_output_chan, n_pulses):
        """
        Run the SMELLIE system in Master Mode (NI Unit provides the trigger signal for both the lasers and the detector) using the PicoQuant Laser Heads
        """
        self.laser_switch.set_active_channel(ls_chan)
        self.laser_driver.set_intensity(intensity)
        self.fibre_switch.set_io_channel_numbers(fs_input_chan, fs_output_chan)
        with TriggerGenerator() as trigGen:
            trigGen.generate_triggers(n_pulses)
        self.go_safe()
        return 0

    def laserheads_slave_mode(self, ls_chan, intensity, fs_input_chan, fs_output_chan, time):
        """
        Run the SMELLIE system in Slave Mode (SNO+ MTC/D provides the trigger signal for both the lasers and the detector) using the PicoQuant Laser Heads
        """
        self.laser_switch.set_active_channel(ls_chan)
        self.laser_driver.set_intensity(intensity)
        self.fibre_switch.set_io_channel_numbers(fs_input_chan, fs_output_chan)
        sleep(time)
        self.go_safe()
        return 0

    def superK_master_mode() # incomplete function!!
        """
        Run the SMELLIE system in Master Mode (NI Unit provides the trigger signal for both the lasers and the detector) using the SuperK Supercontinuum laser
        """
        return 0

    def set_gain_control(self, voltage):
        """
        Set the Gain Voltage of the MPU's PMT ... applicable to both Master and Slave modes and both the Laser Heads and the SuperK laser
        """
        with GainVoltageGenerator() as gainGen:
            gainGen.generate_voltage(voltage)
        return 0

    def log_info(self):
        # pipe info return into logger
        pass

    def set_dummy_mode_on(self, dummy_mode_on = True):
        config.DUMMY_MODE = dummy_mode_on
        return 0

    def info(self):
        pass

    def system_state(self):
        """
        Return a formatted string with the current system settings
        """
        return """ SMELLIE git SHA: {0}
git repository dirty : {1}

CONFIGURATION:
{2}

LASER DRIVER:
{3}

LASER SWITCH:
{4}

FIBRE SWITCH:
{5}

GAIN CONTROL:
{6}
""".format(system_state.get_SHA(),
           True if system_state.git_is_dirty() else False,
           system_state.get_config_str(),
           self.laser_driver.current_state(),
           self.laser_switch.current_state(),
           self.fibre_switch.current_state(),
           self.gain_voltage_gen.current_state()
           )
