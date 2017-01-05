# Test sending an email with a hardware report/status

import logging, time, datetime, smtplib
from smellie import fibre_switch
from email.mime.text import MIMEText

fs = fibre_switch.FibreSwitch()

logging.basicConfig(filename='C:\SMELLIE\logs\test_status_mail.log', filemode="a", level=logging.DEBUG)
console = logging.StreamHandler() #print logger to console
console.setLevel(logging.DEBUG)
logging.getLogger('').addHandler(console)

npass = 0
nfail = 0

try:

    #logging.debug( "Begin Testing SMELLIE Fibre Switch. {}".format( datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') ) )   
    #test current state. (in turn tests many of the getter functions).
    
    #fibreSwitchTest = fs.current_state()
    
    #logging.debug( "FibreSwitch state: {}".format( fibreSwitchTest ) )
 
    #open SMTP connection
    sender = 'jeffrey.lidgard@physics.ox.ac.uk'
    receiver = 'jeffrey.lidgard@balliol.ox.ac.uk'
    message = """test message from smellie alert system."""
    
    msg = MIMEText(message)
    msg['Subject'] = 'message from smellie alert system'
    msg['From'] = sender
    msg['To'] = receiver

    s = smtplib.SMTP('mail.physics.ox.ac.uk',25)
    #username = 'lidgard'
    #password = ''
    #s.starttls()
    #s.login(username, password)
    s.sendmail(sender, receiver, msg.as_string())
    s.quit()
 
    #logging.debug( "Finished Testing SMELLIE Status mail, pass: {}/{}, fail:{}/{}".format(npass,npass+nfail,nfail,npass+nfail) 
    
except Exception, e:
    logging.debug( "Exception:" )
    logging.debug( e )
    
finally:
    pass
