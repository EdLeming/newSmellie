from subprocess import check_output
import config
import os

def get_SHA():
    '''
    Returns the current git SHA of the SMELLIE software
    '''
    return check_output(["git", "describe", "--always", "--tag"]).strip()

def get_config_str():
    """
    Reads the config module into a string
    """
    return "\n".join("{0} : {1}".format(k, v) for (k, v) in config.__dict__.iteritems() if not k.startswith("__"))

