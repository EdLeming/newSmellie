from laser_driver import LaserDriver
from laser_switch import LaserSwitch
from fibre_switch import FibreSwitch
from superk_driver import SuperkDriver
from power_meter import PowerMeter
from ni_trigger_generator import TriggerGenerator
from ni_gain_control import GainVoltageGenerator
from spectrometer import Spectrometer
import system_state
import smellie_config
from time import sleep
from smellie.smellie_logger import SMELLIELogger

class SmellieController(object):
    def __enter__(self):
        """
        Open the SMELLIE Controller, with all hardware in deactivated mode
        """
        SMELLIELogger.debug('SNODROP DEBUG: SmellieController.__enter__()')
        self.fibre_switch = FibreSwitch()
        self.laser_switch = LaserSwitch()
        self.gain_voltage = GainVoltageGenerator()
        self.trig_signals = TriggerGenerator()
        self.laser_driver = LaserDriver()
        self.spectrometer = Spectrometer()
        self.superk_driver = SuperkDriver()
        #self.power_meter = PowerMeter()
        self.laser_driver.port_open()
        self.superk_driver.port_open()
        self.spectrometer.port_open()
        self.fibre_switch.port_open()
        #self.power_meter.port_open()
        
        self.deactivate()
        return self

    def __exit__(self, type, value, traceback):
        """
        Clean up code goes here - it is guaranteed to get called even if an exception is thrown during one of the other functions
        """
        SMELLIELogger.debug('SNODROP DEBUG: SmellieController.__exit__()')
        self.deactivate()
        self.superk_driver.varia_go_safe()
        if self.laser_driver.is_connected(): self.laser_driver.port_close()
        if self.superk_driver.is_connected(): self.superk_driver.port_close()
        if self.spectrometer.is_connected(): self.spectrometer.port_close()
        if self.fibre_switch.is_connected(): self.fibre_switch.port_close()
        #if self.power_meter.is_connected(): self.power_meter.port_close()

    def go_safe(self):
        """
        Send the entire SMELLIE system into `safe mode` - SEPIA soft-lock = on, SEPIA intensity = 0%
        """
        SMELLIELogger.debug('SNODROP DEBUG: SmellieController.go_safe()')
        self.laser_driver.go_safe()
        self.superk_driver.go_safe()
        return 0

    def deactivate(self):
        """
        Send the entire SMELLIE system into `deactivated mode` - SEPIA soft-lock = on, SEPIA intensity = 0%, NI gain voltage = 0V, active Laser Switch channel = 5 (no laser head attached to this channel), Fibre Switch input channel = 5 and output channel = 14 (no detector fibre attached to this output channel, just power meter)
        """       
        SMELLIELogger.debug('SNODROP DEBUG: SmellieController.deactivate()')
        self.go_safe()
        self.gain_voltage.go_safe()
        
        #switch laser switch only if not already set
        ls_chan = self.laser_switch.get_active_channel()
        #print 'laser switch chan:{}'.format(ls_chan)
        if (int(ls_chan) != 5): 
            #print 'Moving laser switch to position:0 (safe position)'
            self.laser_driver.port_close() #close before LaserSwitch d/c
            self.laser_switch.set_active_channel(5)
            self.laser_driver.port_open()
            
        self.fibre_switch.set_io_channel_numbers(5, 14)
        return 0

    def laserheads_master_mode(self, ls_chan, intensity, rep_rate, fs_input_chan, fs_output_chan, n_pulses, gain_voltage):
        """
        Run the SMELLIE system in Master Mode (NI Unit provides the trigger signal for both the lasers and the detector) using the PicoQuant Laser Heads
        
        :param ls_chan: the laser switch channel
        
        :param intensity: the laser intensity in per mil
        
        :param fs_input_channel: the fibre switch input channel

        :param fs_output_channel: the fibre switch output channel

        :param n_pulses: the number of pulses
        """
        
        SMELLIELogger.debug('SNODROP DEBUG: SmellieController.laserheads_master_mode({},{},{},{},{},{},{})'.format(ls_chan, intensity, rep_rate, fs_input_chan, fs_output_chan, n_pulses, gain_voltage))
        #go into safe mode
        self.laser_driver.go_safe()
        
        #switch laser switch only if not already set
        if (self.laser_switch.get_active_channel() != channel): 
            self.laser_driver.port_close() #close before LaserSwitch d/c
            self.laser_switch.set_active_channel(ls_chan)
            self.laser_driver.port_open()

        #set fibre switch channels
        self.fibre_switch.set_io_channel_numbers(fs_input_chan, fs_output_chan)
        
        #set gain voltage
        self.gain_voltage.generate_voltage(gain_voltage)

        #Pulse in master mode
        self.laser_driver.go_ready(intensity)
        self.trig_signals.generate_triggers(n_pulses, rep_rate, 'PQ')

        #go back to safe mode
        self.laser_driver.go_safe()
        return 0

    def laserheads_slave_mode(self, ls_chan, intensity, fs_input_chan, fs_output_chan, time, gain_voltage):
        """
        Run the SMELLIE system in Slave Mode (SNO+ MTC/D provides the trigger signal for both the lasers and the detector) using the PicoQuant Laser Heads

        :param ls_chan: the laser switch channel
        
        :param intensity: the laser intensity in per mil
        
        :param fs_input_channel: the fibre switch input channel

        :param fs_output_channel: the fibre switch output channel

        :param n_pulses: the number of pulses
        
        :param time: time until SNODROP exits slave mode
        """
        SMELLIELogger.debug('SNODROP DEBUG: SmellieController.laserheads_slave_mode({},{},{},{},{},{})'.format(ls_chan, intensity, fs_input_chan, fs_output_chan, time, gain_voltage))
        #go into safe mode
        self.laser_driver.go_safe()
        
        #switch laser switch only if not already set
        if (self.laser_switch.get_active_channel() != channel): 
            self.laser_driver.port_close() #close before LaserSwitch d/c
            self.laser_switch.set_active_channel(ls_chan)
            self.laser_driver.port_open()

        #set fibre switch channels
        self.fibre_switch.set_io_channel_numbers(fs_input_chan, fs_output_chan)
        
        #set gain voltage
        self.gain_voltage.generate_voltage(gain_voltage)

        #Wait in slave mode
        self.laser_driver.go_ready(intensity)
        sleep(time)
        
        #go back to safe mode
        self.laser_driver.go_safe()
        return 0

    def superk_master_mode(self, intensity, rep_rate, low_wavelength, high_wavelength, fs_input_chan, fs_output_chan, n_pulses, gain_voltage):
        """
        Run the SMELLIE system in Master Mode (NI Unit provides the trigger signal for both the lasers and the detector) using the SuperK laser
        
        :param intensity: the laser intensity in per mil
        
        :param fs_input_channel: the fibre switch input channel

        :param fs_output_channel: the fibre switch output channel

        :param n_pulses: the number of pulses
        """
        SMELLIELogger.debug('SNODROP DEBUG: SmellieController.superk_master_mode({},{},{},{},{},{},{},{})'.format(intensity, rep_rate, low_wavelength, high_wavelength, fs_input_chan, fs_output_chan, n_pulses, gain_voltage))
        #go into safe mode
        self.superk_driver.go_safe()
        
        #switch laser_switch only if not already set
        if (self.laser_switch.get_active_channel() != 5): 
            self.laser_driver.port_close() #close before LaserSwitch d/c
            self.laser_switch.set_active_channel(5)
            self.laser_driver.port_open()

        #set fibre switch channels
        self.fibre_switch.set_io_channel_numbers(fs_input_chan, fs_output_chan)
        
        #set gain voltage
        self.gain_voltage.generate_voltage(gain_voltage)
        
        #Pulse in master mode
        self.superk_driver.go_ready(intensity, low_wavelength, high_wavelength)
        self.trig_signals.generate_triggers(n_pulses, rep_rate, 'SUPERK')

        #go back to safe mode
        self.superk_driver.go_safe()
        return 0
        
    def new_run(run_number=-1):
        '''
        Collect the run information from ORCA
        '''
        SMELLIELogger.new_logger('RunNumber_'.format(str(run_number)) )
        SMELLIELogger.debug('SNODROP DEBUG: SmellieController.new_run({})'.format(run_number)

    def log_info(self):
        # pipe info return into logger
        pass

    def set_dummy_mode_on(self, dummy_mode_on = True):
        '''
        Put SNODROP into dummy mode, where all server function calls just result print the call signature
        
        :param dummy_mode_on: True for dummy mode/False for normal functioning
        '''
        smellie_config.DUMMY_MODE = dummy_mode_on
        return 0

    def system_state(self):
        '''
        Return a formatted string with the system settings
        '''
        return "SMELLIE git SHA: {} git repository dirty : {} CONFIGURATION: {} LASER DRIVER: {} SUPERK DRIVER: {} LASER SWITCH: {} FIBRE SWITCH: {} SPECTROMETER: {}".format(system_state.get_SHA(),
           True if system_state.git_is_dirty() else False,
           system_state.get_config_str(),
           self.laser_driver.system_state(),
           self.superk_driver.system_state(),
           self.laser_switch.system_state(),
           self.fibre_switch.system_state(),
           self.spectrometer.system_state()
           )

    def current_state(self):
        '''
        Return a formatted string with the current system settings
        '''
        return "LASER DRIVER: {} \nSUPERK DRIVER: {} \nLASER SWITCH: {} \nFIBRE SWITCH: {} \nGAIN CONTROL: {} \nSPECTROMETER: {}\n".format(self.laser_driver.current_state(),
        self.superk_driver.current_state(),
        self.laser_switch.current_state(),
        self.fibre_switch.current_state(),
        self.gain_voltage.current_state(),
        self.spectrometer.current_state()
        )
        

