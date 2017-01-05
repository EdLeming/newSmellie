# Test sending a hardware status message via scp (requires a ssh key)

import logging, time, datetime
from smellie import fibre_switch

import paramiko
paramiko.util.log_to_file('C:\SMELLIE\logs\test_status_scp_login.log')

fs = fibre_switch.FibreSwitch()

logging.basicConfig(filename='C:\SMELLIE\logs\test_status_scp.log', filemode="a", level=logging.DEBUG)
console = logging.StreamHandler() #print logger to console
console.setLevel(logging.DEBUG)
logging.getLogger('').addHandler(console)

npass = 0
nfail = 0

try:

    #logging.debug( "Begin Testing SMELLIE Fibre Switch. {}".format( datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') ) )   
    #test current state. (in turn tests many of the getter functions).
    
    fibreSwitchTest = fs.current_state()
    
    logging.debug( "FibreSwitch state: {}".format( fibreSwitchTest ) )
 
    #logging.debug( "Finished Testing SMELLIE Status mail, pass: {}/{}, fail:{}/{}".format(npass,npass+nfail,nfail,npass+nfail) )
    
except Exception, e:
    logging.debug( "Exception:" )
    logging.debug( e )
    
finally:
    #open SSH connection
    myhost = 'pplxint9.physics.ox.ac.uk'
    myport = 22
    myuser = 'lidgard'
    mykey = paramiko.RSAKey.from_private_key_file('C:\SMELLIE\software\smelliekey.prv')
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(myhost, myport, username = myuser, pkey = mykey)
    sftp = ssh.open_sftp()

    #send file
    filepath = '/home/lidgard/SMELLIE/test_status_scp.log'
    localpath = 'C:\SMELLIE\logs\test_status_scp.log'
    sftp.put(localpath, filepath)

    #close connections
    sftp.close()
    ssh.close()