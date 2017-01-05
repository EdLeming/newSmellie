# Test the SMELLIE controller
# loads the controller (opens all HW)
# test by printing current state

import logging, time, datetime
from smellie.smellie_controller import SmellieController

logging.basicConfig(filename=r'C:\SMELLIE\logs\test_smellie_controller.log', filemode="a", level=logging.DEBUG)
console = logging.StreamHandler() #print logger to console
console.setLevel(logging.DEBUG)
logging.getLogger('').addHandler(console)

logging.debug( "Begin Testing SMELLIE controller. {}".format( datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') ) )  

with SmellieController() as controller:
    logging.debug('Current state: \n{}'.format(controller.current_state()))
    
logging.debug( "Finished Testing SMELLIE controller. {}".format(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') ) )
