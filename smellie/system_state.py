from subprocess import check_output
import smellie_config
import os

def get_SHA():
    """
    Returns the current git SHA of the SMELLIE software
    """
    return check_output(["git", "describe", "--always", "--tag"]).strip()

def git_is_dirty():
    '''
    Are there any uncommited changes in the repository?
    '''
    return True if check_output(["git", "status", "--porcelain"]) else False

def get_config_str():
    '''
    Reads the config.py module (located one folder-level up from this file) into a string
    '''
    return "\n".join("{0} : {1}".format(k, v) for (k, v) in smellie_config.__dict__.iteritems() if not k.startswith("__"))

