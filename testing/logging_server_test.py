# Test the snotdaq logging server functionality
# to echo commands received by the logging server, run the 'tail_daq_log' script (in venv\Scripts)

import logging, time, datetime
from smellie import fibre_switch
from snotdaq import Logger
from smellie_config import LOGGER_SERVER, LOGGER_PORT

fs = fibre_switch.FibreSwitch()
log = Logger()

#create local log file
log.set_logfile('C:\SMELLIE\logs\test_logging_server.log')

#connect to logging server
log.connect('smellie',LOGGER_SERVER,LOGGER_PORT)

try:
    log.debug( "Begin Testing SMELLIE system with logging server. {}".format( datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') ) )   
    
    #open SMELLIE server
    fs.port_open()
    
    #Test1: Current state
    log.debug( "Test current state: \n{}".format( fs.current_state() ) )
    
    #close superk 
    fs.port_close()

    log.debug( "Finished Testing SMELLIE system with logging server. {}".format(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') ) )
    
except Exception, e:
    logging.debug( "Exception:" )
    logging.debug( e )