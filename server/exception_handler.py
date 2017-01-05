"""
Processes exceptions thrown by the software, converting them to error strings to be sent over the server
"""
from functools import wraps
from smellie.smellie_logger import SMELLIELogger

HANDLED_EXCEPTIONS = []

def log_exception(exception_string):
    """
    Logs exceptions to logging server at highest level (warn).

    :param exception: The exception to log
    """
    SMELLIELogger.warn(exception_string)

def process_exception(exception):
    """
    Translates exceptions to error strings.
    This returns SNODROP Exception: <string representation of exception> for handled exceptions, or SNODROP Unhandled Exception!!: <string representation of exception> for unhandled ones.

    :param exception: The exception to process

    :returns: An error string
    """
    thrown_type = exception.__class__
    if thrown_type in HANDLED_EXCEPTIONS:
        return "SNODROP ERROR: {0}".format(repr(exception))
    return "SNODROP ERROR: Unhandled exception!! {0}".format(repr(exception))

def str_wrap_exceptions(orig_function):
    """
    Function wrapper to catch any exceptions and return an error string using :func:`process_exception`

    :param orig_function: The function to wrap

    :returns: A logically equivalent function, that returns an error string rather than raising exceptions.
    """
    @wraps(orig_function)
    def modified_function(*args, **kwargs):
        try:
            return orig_function(*args, **kwargs)
        except Exception as e:
            e_string = process_exception(e)
            log_exception(e_string)
            return e_string
    return modified_function
