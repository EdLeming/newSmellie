# Dummy mode just prints the signature of calls to server functions
DUMMY_MODE = False

# SEPIA Laser Driver
SEPIA_DLL_PATH        = "C:\\Program Files\\PicoQuant\\GenericLaserDriver\\API\\x64\\Sepia2_Lib.dll"
SEPIA_STR_BUFFER_SIZE = 128  # must be at minimum = 64 bytes
PQ_DRIVER_DEV_ID   = 0
PQ_SLOT_ID  = 200
PQ_DRIVER_SLOT_ID  = 0

# Smellie Controller Server
ADDRESS = "0.0.0.0"
PORT = 5020

# Logging Server
LOGGER_SERVER = 'minard.sp.snolab.ca'
LOGGER_PORT = 4001
LOGGER_CONNECT_TO_SERVER = False

# Fibre Switch (70 channel)
FIBRE_SWITCH_SERIAL_PORT = 14 # = actually COM6 6(i.e. value = COM number - 1)
FIBRE_SWITCH_BAUD_RATE   = 57600
FIBRE_SWITCH_WAIT_TIME   = 0.1  # in seconds

# Fibre Switch (4 channel)
FIBRE_SWITCH_4CHAN_SERIAL_PORT = 17 # = actually COM6 6(i.e. value = COM number - 1)
FIBRE_SWITCH_4CHAN_BAUD_RATE   = 57600
FIBRE_SWITCH_4CHAN_WAIT_TIME   = 0.1  # in seconds

# Laser Switch
LASER_SWITCH_SERIAL_PORT = 13 # = actually COM14 (i.e. value = COM number - 1)
LASER_SWITCH_BAUD_RATE   = 9600
LASER_SWITCH_WAIT_TIME   = 0.1  # in seconds
LASER_SWITCH_EXECUTE_TIME   = 20 # in seconds

# Interlock
INTERLOCK_SERIAL_PORT = 0
INTERLOCK_BAUD_RATE = 9600
INTERLOCK_WAIT_TIME   = 0.1  # in seconds

# Laser Switch
RELAY_COM_CHANNEL = 1
RELAY_SLEEP       = 45  # in seconds
RESET_NAME = "*ROOT_HUB30*"

# NI Unit - Gain Control and Trigger Generator
NI_DEV_NAME               = "Dev1"
GAIN_CONTROL_N_SAMPLES    = 100
GAIN_CONTROL_SAMP_FREQ    = 3000
GAIN_CONTROL_PIN_OUT      = "/ao0"
GAIN_CONTROL_VOLTAGE_OFFSET = 0.0044
MPU_SAMPLE_N_SAMPLES    = 100000
MPU_SAMPLE_SAMP_FREQ    = 100000
MPU_SAMPLE_PIN_IN      = "/ai1"
TRIG_GEN_HIGH_TIME        = 0.0000005  # in seconds
TRIG_GEN_MAX_FREQUENCY        = 100000  # in Hz
TRIG_GEN_MINIMUM_LOW_TIME = 0.000005  # in seconds
TRIG_GEN_PIN_OUT_PQ          = "/Ctr0"
TRIG_GEN_PIN_OUT_SUPERK      = "/Ctr1"

# Power Meter
PM_ADDRESS = "USB0::0x1313::0x8070::P0005368::INSTR"
PM_DLL_PATH = r"C:\SMELLIE\software\LabView\compiled libraries\powerMeterUtil.dll"
PM_STR_BUFFER_SIZE = 128

# Spectrometer
SPEC_DLL_PATH = r"C:\SMELLIE\software\LabView\compiled libraries\OOUtil.dll"
SPEC_STR_BUFFER_SIZE = 128

# SuperK Laser
SK_COM_PORT = "COM4"
SK_DLL_PATH = r"C:\SMELLIE\software\LabView\compiled libraries\superKUtil.dll"
SK_STR_BUFFER_SIZE = 128
SK_MAX_INT_FREQUENCY = 20000
SK_ND_FILTER_SERIAL_PORT = 7  # = actually COM8(i.e. COM number-1)
SK_ND_FILTER_BAUD_RATE = 57600
SK_ND_FILTER_WAIT_TIME   = 0.1  # in seconds

# DAQMX Library
FILE_LOC_WINXP      = r"C:\Program Files (x86)\National Instruments\NI-DAQ\DAQmx ANSI C Dev\include\NIDAQmx.h"  # full path of the NIDAQmx.h file if installed on Windows XP
FILE_LOC_WIN7_64BIT = r"C:\Program Files (x86)\National Instruments\NI-DAQ\DAQmx ANSI C Dev\include\NIDAQmx.h"  # full path of the NIDAQmx.h file if installed on Windows 7 64-bit
FILE_LOC_LINUX      = "/usr/local/natinst/nidaqmx/include/NIDAQmx.h"  # full path of the NIDAQmx.h file if installed on Linux
LIB_NAME_WIN        = "nicaiu" # name and path of the library if installed on Windows (any version)
LIB_NAME_LINUX      = "libnidaqmx.so"  # name and path of the library if installed on Linux (to find it, use the command: `find_library('nidaqmx')`
