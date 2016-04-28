from laser_driver import LaserDriver
from laser_switch import LaserSwitch
from fibre_switch import FibreSwitch
from time import sleep
from ni_box import TriggerGenerator, GainVoltageGenerator
import system_state

class SmellieController(object):    
    def __enter__(self):
        """
        Open the SMELLIE CONTROLLER, with hardware in deactivated mode
        """        
        self.fibre_switch = FibreSwitch()              
        self.laser_switch = LaserSwitch()              
        self.gain_voltage_gen = GainVoltageGenerator() 
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
        self.laser_driver.go_safe()
        self.gain_voltage_gen.go_safe()
        return 0

    def deactivate(self):
        self.go_safe()
        self.laser_switch.set_active_channel(0)
        return 0

    def pulse_master_mode(self, freq, n_pulses, fs_input_chan, fs_output_chan, ls_chan, intensity):
        self.laser_switch.set_active_channel(ls_chan)
        self.laser_driver.set_intensity(intensity)
        self.fibre_switch.set_io_channel_numbers(input_channel, output_channel)

        with TriggerGenerator() as trig:
            trig.generate(n_pulses)

        self.go_safe()
        return 0

    def enter_slave_mode(self, fs_input_chan, fs_output_chan, ls_chan, intensity, time):
        self.laser_switch.set_active_channel(ls_chan)
        self.laser_driver.set_intensity(intensity)
        self.fibre_switch.set_io_channel_numbers(fs_input_chan, fs_output_chan)
        sleep(time)
        self.go_safe()
        return 0

    def set_gain_control(self, voltage):
        with GainVoltageGenerator() as g:
            g.set_voltage(voltage)
        return 0

    def system_state(self):
        return """ SMELLIE git SHA: {0}
CONFIGURATION:
{1}

LASER DRIVER:
{2}

LASER SWITCH:
{3}

FIBRE SWITCH:
{4}

GAIN CONTROL:
{5}
""".format(system_state.get_SHA(),
           system_state.get_config_str(),
           self.laser_driver.current_state(),
           self.laser_switch.current_state(),
           self.fibre_switch.current_state(),
           self.gain_voltage_gen.current_state())
