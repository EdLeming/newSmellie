# SEPIA Laser Driver
SEPIA_DLL_PATH        = "C:\Users\LocalAdmin\Desktop\Pysepia\Sepia2_Lib.dll"
SEPIA_STR_BUFFER_SIZE = 128  # must be at minimum = 64 bytes
LASER_DRIVER_DEV_ID   = 0
LASER_DRIVER_SLOT_ID  = 200

# Server
PORT = 5020

# Fibre Switch 
FIBRE_SWITCH_SERIAL_PORT = 0
FIBRE_SWITCH_BAUD_RATE   = 57600
FIBRE_SWITCH_WAIT_TIME   = 0.1  # in seconds

# Interlock
INTERLOCK_PORT      = 3  # = COM4
INTERLOCK_BAUD_RATE = 57600

# Laser Switch
RELAY_COM_CHANNEL = 1
RELAY_SLEEP       = 30  # in seconds

# NI Unit - Gain Control and Trigger Generator
NI_DEV_NAME               = "Dev1"
GAIN_CONTROL_N_SAMPLES    = 100
GAIN_CONTROL_SAMP_FREQ    = 3000
GAIN_CONTROL_PIN_OUT      = "/ao0"
TRIG_GEN_HIGH_TIME        = 0.0000005  # in seconds
TRIG_GEN_FREQUENCY        = 1000  # in Hz
TRIG_GEN_MINIMUM_LOW_TIME = 0.0001  # in seconds
TRIG_GEN_PIN_OUT          = "/Ctr0"
