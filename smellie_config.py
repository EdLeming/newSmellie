# Dummy mode just prints the signature of calls to server functions
DUMMY_MODE = True

# SEPIA Laser Driver
#"C:\Program Files\PicoQuant\GenericLaserDriver\Sepia2_Lib.dll"
#"C:\Program Files (x86)\PicoQuant\Sepia II\Demos\MSVCPP\Shared_MSVCPP\Sepia2_Lib.dll"
SEPIA_DLL_PATH        = "C:\\Program Files\\PicoQuant\\GenericLaserDriver\\API\\x64\\Sepia2_Lib.dll"
SEPIA_STR_BUFFER_SIZE = 128  # must be at minimum = 64 bytes
LASER_DRIVER_DEV_ID   = 0
LASER_SLOT_ID  = 200
LASER_DRIVER_SLOT_ID  = 0

# Smellie Controller Server
ADDRESS = "0.0.0.0"
PORT = 5020

# Logging Server
LOGGER_PORT = 0

# Fibre Switch 
FIBRE_SWITCH_SERIAL_PORT = 8 # = COM9
FIBRE_SWITCH_BAUD_RATE   = 57600
FIBRE_SWITCH_WAIT_TIME   = 0.1  # in seconds

# Interlock
INTERLOCK_SERIAL_PORT = 7  # = COM8
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
TRIG_GEN_HIGH_TIME        = 0.0000005  # in seconds
TRIG_GEN_FREQUENCY        = 1000  # in Hz
TRIG_GEN_MINIMUM_LOW_TIME = 0.0001  # in seconds
TRIG_GEN_PIN_OUT_PQ          = "/Ctr0"
TRIG_GEN_PIN_OUT_SUPERK      = "/Ctr1"

# Power Meter
PM_ADDRESS = "USB0::0x1313::0x8078::P0005368::INSTR"
PM_DLL_PATH = r"C:\SMELLIE\software\newSmellie\powermeter\powerMeterUtil.dll"
PM_STR_BUFFER_SIZE = 128

# Spectrometer
SPEC_DLL1_PATH = r"C:\SMELLIE\software\newSmellie\spec\OOUtil.dll"
SPEC_DLL2_PATH = r"C:\Program Files\Ocean Optics\OmniDriver\OOI_HOME\common64.dll"
SPEC_STR_BUFFER_SIZE = 128

# DAQMX Library
FILE_LOC_WINXP      = r"C:\Program Files (x86)\National Instruments\NI-DAQ\DAQmx ANSI C Dev\include\NIDAQmx.h"  # full path of the NIDAQmx.h file if installed on Windows XP
FILE_LOC_WIN7_64BIT = r"C:\Program Files (x86)\National Instruments\NI-DAQ\DAQmx ANSI C Dev\include\NIDAQmx.h"  # full path of the NIDAQmx.h file if installed on Windows 7 64-bit
FILE_LOC_LINUX      = "/usr/local/natinst/nidaqmx/include/NIDAQmx.h"  # full path of the NIDAQmx.h file if installed on Linux
LIB_NAME_WIN        = "nicaiu" # name and path of the library if installed on Windows (any version)
LIB_NAME_LINUX      = "libnidaqmx.so"  # name and path of the library if installed on Linux (to find it, use the command: `find_library('nidaqmx')`
