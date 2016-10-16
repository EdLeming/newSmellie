import daqmx.functions
import daqmx.constants
from smellie_config import NI_DEV_NAME, TRIG_GEN_HIGH_TIME, TRIG_GEN_MINIMUM_LOW_TIME, TRIG_GEN_MAX_FREQUENCY, TRIG_GEN_MINIMUM_LOW_TIME, TRIG_GEN_PIN_OUT_PQ, TRIG_GEN_PIN_OUT_SUPERK
from ctypes import byref

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
    
    def _setup(self):
        """
        Set up the single-pulse parameters - the high time and the low time, and the digital output channel X to be used.
        The channel string must be of the form `deviceName/digitalOutputPin`, i.e. `Dev1/Ctr0`.  /Ctr0 is used by default, but can be changed in config.py if required.
        """
        self.high_time = TRIG_GEN_HIGH_TIME
        self.low_time = (1.0 / self.frequency) - self.high_time
        if self.low_time < TRIG_GEN_MINIMUM_LOW_TIME:
            self.low_time = TRIG_GEN_MINIMUM_LOW_TIME
        self.dev_name = NI_DEV_NAME

        self.taskHandle = daqmx.functions.TaskHandle(0)
        daqmx.functions.DAQmxCreateTask("", byref(self.taskHandle))
        daqmx.functions.DAQmxCreateCOPulseChanTime(self.taskHandle, self.dev_name + self.trig_out_pin, "", daqmx.constants.DAQmx_Val_Seconds, daqmx.constants.DAQmx_Val_Low, 0.0, self.low_time, self.high_time)

    def _cleanup(self):
        """
        Wait until all n trigger pulses have been sent, and then stop the Trigger Generation task and clear the NI Unit's task memory.
        """
        if self.taskHandle is not None:
            daqmx.functions.DAQmxStopTask(self.taskHandle)
            daqmx.functions.DAQmxClearTask(self.taskHandle)
        self.taskHandle = None
        
    def set_trigger_destination(self, name):
        if name=="SUPERK": 
            self.trig_out_pin = TRIG_GEN_PIN_OUT_SUPERK
        elif name=="PQ": 
            self.trig_out_pin = TRIG_GEN_PIN_OUT_PQ
        else: 
            raise ValueError("Select either SUPERK or PQ")
            
    def set_repetition(self, frequency):
        if frequency <= TRIG_GEN_MAX_FREQUENCY and frequency>0:
            self.frequency = frequency
        else: 
            raise NILogicError("Requested frequency too high.")
        
    def generate_triggers(self, n_pulses, repetition_rate, destination):
        """
        Start the Trigger Generation task using the single-pulse parameters previously set up in the __enter__ function, and the requested number of pulses
        :param n_pulses:
        """
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
