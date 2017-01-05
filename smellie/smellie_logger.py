from smellie_config import LOGGER_SERVER, LOGGER_PORT, LOGGER_CONNECT_TO_SERVER
from snotdaq import Logger
import time,datetime 

"""
Interface with the SNOTDAQ Logger
"""

class SMELLIELoggerLogicError(Exception):
    """
    Thrown if an inconsistency is noticed *after* any hardware instruction is executed (i.e. a problem with the hardware itself)
    """
    pass

class SMELLIELogger(object):

    the_logger = None  
    def __init__(self):
        raise SMELLIELoggerLogicError("Do not initiate object. Use classes only.")

    @classmethod
    def new_logger(cls, name):
        """
        Create a new logger
        """
        cls.the_logger = Logger()
        
        if LOGGER_CONNECT_TO_SERVER:
           cls.connect()

        cls.the_logger.set_logfile('C:\SMELLIE\logs\smellie_logger_{}_time{}.log'.format( name, datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d_%H%M%S') ) )  #write local log 
  
    @classmethod    
    def connect(cls):
        cls.the_logger.connect('SMELLIE-JEFF_TESTING',LOGGER_SERVER,LOGGER_PORT) #connect to logging server
   
    @classmethod
    def debug(cls, *args, **kwargs):
        cls.check_handle()
        cls.the_logger.debug(*args, **kwargs)
        
    @classmethod
    def verbose(cls,*args, **kwargs):
        cls.check_handle()
        cls.the_logger.verbose(*args, **kwargs)
    
    @classmethod
    def notice(cls,*args, **kwargs):
        cls.check_handle()
        cls.the_logger.notice(*args, **kwargs)
    
    @classmethod
    def warn(cls,*args, **kwargs):
        cls.check_handle()
        cls.the_logger.warn(*args, **kwargs)
    
    @classmethod
    def check_handle(cls):
        if cls.the_logger is None:
            cls.new_logger("undefined")