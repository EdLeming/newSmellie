import daqmx.functions,daqmx.constants
from smellie_config import NI_DEV_NAME, TRIG_GEN_HIGH_TIME, TRIG_GEN_MINIMUM_LOW_TIME, TRIG_GEN_MAX_FREQUENCY, TRIG_GEN_MINIMUM_LOW_TIME, TRIG_GEN_PIN_OUT_PQ, TRIG_GEN_PIN_OUT_SUPERK
from ctypes import byref, c_ulong, create_string_buffer
from smellie.smellie_logger import SMELLIELogger

"""
Generation of the SEPIA and SuperK trigger signals using the National Instruments (NI) Unit
"""
class NILogicError(Exception):
    """
    Thrown if an inconsistency is noticed *before* any instructions are sent to the hardware (i.e. a problem with code logic)
    """
    pass
    
class TriggerGenerator(object):
    """
    Controls the SEPIA and SuperK trigger signals, as produced by the NI Unit via commands sent down a USB port.
    """
    def __init__(self):
        self.taskHandle = None
        self.dev_name = NI_DEV_NAME
    
    def _setup(self):
        """
        Set up the single-pulse parameters - the high time and the low time, and the digital output channel X to be used.
        The channel string must be of the form `deviceName/digitalOutputPin`, i.e. `Dev1/Ctr0`.  /Ctr0 is used by default, but can be changed in config.py if required.
        """
        SMELLIELogger.debug('SNODROP DEBUG: TriggerGenerator._setup()')
        self.high_time = TRIG_GEN_HIGH_TIME
        self.low_time = (1.0 / self.frequency) - self.high_time
        if self.low_time < TRIG_GEN_MINIMUM_LOW_TIME:
            self.low_time = TRIG_GEN_MINIMUM_LOW_TIME

        self.taskHandle = daqmx.functions.TaskHandle(0)
        daqmx.functions.DAQmxCreateTask("", byref(self.taskHandle))
        daqmx.functions.DAQmxCreateCOPulseChanTime(self.taskHandle, self.dev_name + self.trig_out_pin, "", daqmx.constants.DAQmx_Val_Seconds, daqmx.constants.DAQmx_Val_Low, 0.0, self.low_time, self.high_time)

    def _cleanup(self):
        """
        Wait until all n trigger pulses have been sent, and then stop the Trigger Generation task and clear the NI Unit's task memory.
        """
        SMELLIELogger.debug('SNODROP DEBUG: TriggerGenerator._cleanup()')
        if self.taskHandle is not None:
            daqmx.functions.DAQmxStopTask(self.taskHandle)
            daqmx.functions.DAQmxClearTask(self.taskHandle)
        self.taskHandle = None
        
    def set_trigger_destination(self, name):
        """
        Set the appropriate NI DAQ output channel for either laser system. 
        
        :params: "SUPERK" or "PQ"
        """
        SMELLIELogger.debug('SNODROP DEBUG: TriggerGenerator.set_trigger_destination({})'.format(name))
        if name=="SUPERK": 
            self.trig_out_pin = TRIG_GEN_PIN_OUT_SUPERK
        elif name=="PQ": 
            self.trig_out_pin = TRIG_GEN_PIN_OUT_PQ
        else: 
            raise ValueError("Select either SUPERK or PQ")
            
    def set_repetition(self, frequency):
        """
        Set the repetition rate of the generated triggers.
        
        :params: frequency
        """
        SMELLIELogger.debug('SNODROP DEBUG: TriggerGenerator.set_repetition({})'.format(frequency))
        if frequency <= TRIG_GEN_MAX_FREQUENCY and frequency>0:
            self.frequency = frequency
        else: 
            raise NILogicError("Requested frequency too high.")
        
    def generate_triggers(self, n_pulses, repetition_rate, destination):
        """
        Start the Trigger Generation task using the single-pulse parameters previously set up in the __enter__ function, and the requested number of pulses
        
        :param n_pulses, repetition_rate, destination
        """
        SMELLIELogger.debug('SNODROP DEBUG: TriggerGenerator.generate_triggers({}, {},{})'.format(n_pulses, repetition_rate, destination))
        self.set_trigger_destination(destination)
        self.set_repetition(repetition_rate)
        try:
            self._setup()
            daqmx.functions.DAQmxCfgImplicitTiming(self.taskHandle, daqmx.constants.DAQmx_Val_FiniteSamps, n_pulses)
            daqmx.functions.DAQmxStartTask(self.taskHandle)
            daqmx.functions.DAQmxWaitUntilTaskDone(self.taskHandle, -1) # second argument needs checking
            #time out should be rate of triggers * no of triggers, not -1.
        finally:
            self._cleanup()

    def is_connected(self):
        """
        Check if the connection to the device is open
        For the NI device, this just calls is_alive()
        """
        return self.is_alive()
        
    def is_alive(self):
        """
        Quick check alive or not.
        """
        isAlive = None
        checkValue = c_ulong()
        str_buf = create_string_buffer(20)
        daqmx.functions.DAQmxGetDevProductType(self.dev_name, str_buf, 20) #choose to check the HW model and serial ('USB-6211', '0x180a5e6' in hex)
        daqmx.functions.DAQmxGetDevSerialNum(self.dev_name, byref(checkValue)) 
        if (str_buf.value=='USB-6211' and hex(checkValue.value)=='0x180a5e6L'): isAlive = True
        else: isAlive = False
        return isAlive