"""
A personally opinionated logging package.
LICENSE MIT Copyright 2023 Akhlak Mahmood

"""

__version__ = "0.1.2"
__author__ = "Akhlak Mahmood"

import os
import sys
import time
import textwrap
from datetime import datetime, timezone

FATAL = 1
ERROR = 2
WARN  = 3
NOTE  = 4
DONE  = 5
INFO  = 6
TRACE = 7
DEBUG = 8

_prefixes = {
    FATAL: "CRITICAL", # process must exit
    ERROR: "ERROR --", # irrecoverable error
    WARN:  "WARN  --", # unexpected or rare condition
    NOTE:  "NOTE  --", # special notes
    DONE:  "  OK  --", # success message, trace
    INFO:  "      --", # info messages, default level
    TRACE: "  --  --", # start of something, trace
    DEBUG: "DEBUG --", # for development
}

_reset_seq = "\033[0m"
_red, _green, _yellow, _blue, _magenta, _cyan, _white = range(31, 38)

_color_seqs = {
    FATAL:  "\033[1;%dm" % _red,
    ERROR:  "\033[1;%dm" % _yellow,
    WARN:   "\033[0;%dm" % _magenta,
    NOTE:   "\033[1;%dm" % _cyan,
    DONE:   "\033[0;%dm" % _yellow,
    INFO:   "\033[1;%dm" % _cyan,
    TRACE:  "\033[0;%dm" % _white,
    DEBUG:  "\033[1;%dm" % _white,
}

class _config(object):
    logger = ""       # name of the logger
    level = INFO      # cofigured log level
    max_length = 200  # maximum length of a formatted message
    file_times      = True      # show times or not
    console_times   = False     # show times or not
    time_fmt = "%y-%m-%d %Z %I:%M:%S %p"
    color = True      # show colors or not
    fileh = None      # handle to a logfile
    file_stack = False     # save caller info to logfile or not
    console_stack = False  # show caller info on console or not
    line_width = 100    # fix width of the log messages
    _lastInfoTime = None # pvt var to measure execution time

# Global module variables.
_conf = _config()
_manager = {}
_levelOverrides = {}

class Timer:
    """
    Usage:
        st = logg.info("Starting download --", id=23)
        st.done("Downloaded {id}, size {size} K.", size=1024)
    """
    def __init__(self, conf, **kwargs) -> None:
        self._start = time.time()
        self._conf = conf
        self._kwargs = kwargs

    def elapsed(self):
        """ Return time elapsed since the start of the timer. """
        return time.time() - self._start

    def done(self, msg, *args, **kwargs):
        """ Log a done message for the task. """
        self._kwargs.update(kwargs)
        self._kwargs['time_elapsed'] = self.elapsed()
        _log(self._conf, DONE, _stack_info(), msg, *args, **self._kwargs)


class _new(_config):
    """
    Intialize a new named logger.

    """
    def __init__(self, name) -> None:
        super().__init__()
        self.conf = {
            'logger' : name
        }

    def update(self, key, value):
        """ Set individual setting of the named logger. """
        avail = [v for v in vars(_config) if not v.startswith("_")]
        if key in avail:
            self.conf[key] = value
        else:
            raise AttributeError("Unknown setting: '%s'\nAvailable: %s" %(key, avail))
        return self

    def _log(self, level, stack, msg, *args, **kwargs):
        # Update with the module level configurations.
        self.__dict__.update(_conf.__dict__)
        # Update with sub-logger level configurations.
        self.__dict__.update(self.conf)
        if self.level < level:
            return
        _log(self, level, stack, msg, *args, **kwargs)

    def fatal(self, msg, *args, **kwargs):
        self._log(FATAL, _stack_info(), msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        self._log(FATAL, _stack_info(), msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self._log(ERROR, _stack_info(), msg, *args, **kwargs)

    def warn(self, msg, *args, **kwargs):
        self._log(WARN, _stack_info(), msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self._log(WARN, _stack_info(), msg, *args, **kwargs)

    def note(self, msg, *args, **kwargs) -> Timer:
        self._log(NOTE, _stack_info(), msg, *args, **kwargs)
        return Timer(self, **kwargs)

    def done(self, msg, *args, **kwargs):
        self._log(DONE, _stack_info(), msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs) -> Timer:
        self._log(INFO, _stack_info(), msg, *args, **kwargs)
        return Timer(self, **kwargs)

    def trace(self, msg, *args, **kwargs) -> Timer:
        self._log(TRACE, _stack_info(), msg, *args, **kwargs)
        return Timer(self, **kwargs)

    def debug(self, msg, *args, **kwargs):
        self._log(DEBUG, _stack_info(), msg, *args, **kwargs)


def New(name) -> _new:
    """
    Get the logger with name or create a new named logger.
    """
    if not name in _manager:
        log = _new(name)
        _manager[name] = log
    return _manager[name]


def _colorize(conf, level, msg):
    if not conf.color:
        return msg
    return f"{_color_seqs[level]}{msg}{_reset_seq}"

def _save(conf, level, fmtmsg, timestr, caller):
    if conf.fileh is None:
        return

    if not conf.file_times:
        timestr = ""

    extra = ""
    if conf.file_stack or level in [FATAL, DEBUG]:
        extra += caller

    prefix = _prefixes[level]
    fmtlogger = f"{conf.logger}_ " if conf.logger else ""
    line = f"{timestr} {prefix} {fmtlogger}{fmtmsg} {extra}"
    line = _indent(conf, line)

    conf.fileh.write(line + "\n")
    conf.fileh.flush()
    return line

def _print(conf, level, fmtmsg, timestr, caller):
    if not conf.console_times:
        timestr = ""

    extra = ""
    if conf.console_stack or level in [FATAL, DEBUG]:
        extra += caller

    prefix = _colorize(conf, level, _prefixes[level])
    if level in [FATAL, ERROR, DEBUG]:
        fmtmsg = _colorize(conf, level, fmtmsg)

    fmtlogger = f"{conf.logger}_ " if conf.logger else ""
    line = f"{timestr} {prefix} {fmtlogger}{fmtmsg} {extra}"
    line = _indent(conf, line)
    print(line)
    return line

def _log(conf, level : int, stack : tuple, msg : str, *args, **kwargs):
    if _conf.level < level:
        return
    
    if conf.logger in _levelOverrides:
        if _levelOverrides[conf.logger] < level:
            return

    # Caller info
    lineno = stack[1]
    funcname = stack[2]
    filepath = stack[0]
    caller = f"[{funcname} {filepath}:{lineno}]"

    # Date time info
    local_now = datetime.now(timezone.utc).astimezone()
    timestr = local_now.strftime(f"[{_conf.time_fmt}]")

    try:
        fmtmsg = msg.format(*args, **kwargs)
    except:
        fmtmsg = msg
    fmtmsg = _shorten(conf, fmtmsg)

    # Timer info
    if 'time_elapsed' in kwargs:
        fmtmsg = f"{fmtmsg} (took {kwargs['time_elapsed']:.3f} s)"

    _save(conf, level, fmtmsg, timestr, caller)
    _print(conf, level, fmtmsg, timestr, caller)


def fatal(msg, *args, **kwargs):
    _log(_conf, FATAL, _stack_info(), msg, *args, **kwargs)

def critical(msg, *args, **kwargs):
    _log(_conf, FATAL, _stack_info(), msg, *args, **kwargs)

def error(msg, *args, **kwargs):
    _log(_conf, ERROR, _stack_info(), msg, *args, **kwargs)

def warn(msg, *args, **kwargs):
    _log(_conf, WARN, _stack_info(), msg, *args, **kwargs)

def warning(msg, *args, **kwargs):
    _log(_conf, WARN, _stack_info(), msg, *args, **kwargs)

def note(msg, *args, **kwargs) -> Timer:
    _log(_conf, NOTE, _stack_info(), msg, *args, **kwargs)
    return Timer(_conf, **kwargs)

def done(msg, *args, **kwargs):
    _log(_conf, DONE, _stack_info(), msg, *args, **kwargs)

def info(msg, *args, **kwargs) -> Timer:
    _log(_conf, INFO, _stack_info(), msg, *args, **kwargs)
    return Timer(_conf, **kwargs)

def trace(msg, *args, **kwargs) -> Timer:
    _log(_conf, TRACE, _stack_info(), msg, *args, **kwargs)
    return Timer(_conf, **kwargs)

def debug(msg, *args, **kwargs):
    _log(_conf, DEBUG, _stack_info(), msg, *args, **kwargs)

def close():
    """ Shutdown logging. Close any open handles. """
    _log(_conf, DONE, _stack_info(), "~")
    if _conf.fileh is not None:
        _conf.fileh.close()
        _conf.fileh = None

def setFile(file_handle):
    """ Set the file handle of the log file. """
    _conf.fileh = file_handle

def setLevel(level):
    """
    Set the level of the main logger.
    This has the highest precedence even before the overrides.    
    """
    _conf.level = level

def setLoggerLevel(name, level : int):
    """ Override the level of a named logger. """
    _levelOverrides[name] = level

def setMaxLength(length : int):
    """ Max allowed length of a log message. """
    _conf.max_length = length

def setConsoleStack(*, show : bool = None):
    """
    Show caller info on console for all levels.
    Caller info are automatically shown for fatal and debug messages.
    """
    if show is not None:
        _conf.console_stack = show

def setFileStack(*, show : bool = None):
    """
    Write caller info to log file for all levels.
    Caller info are automatically write for fatal and debug messages.
    """
    if show is not None:
        _conf.file_stack = show

def setConsoleTimes(*, show : bool = None, fmt : str = None):
    """ Show times on console. """
    if show is not None:
        _conf.console_times = show
    if fmt is not None:
        _conf.console_time_fmt = fmt

def setFileTimes(*, show : bool = None, fmt : str = None):
    """ Write times to log file. """
    if show is not None:
        _conf.file_times = show
    if fmt is not None:
        _conf.file_time_fmt = fmt


if hasattr(sys, "_getframe"):
    currentframe = lambda: sys._getframe(1)
else:
    def currentframe():
        """Return the frame object for the caller's stack frame."""
        try:
            raise Exception
        except Exception:
            return sys.exc_info()[2].tb_frame.f_back

def _stack_info(stacklevel=1):
    try:
        raise Exception
    except Exception:
        f = sys.exc_info()[2].tb_frame.f_back

    if f is None:
        return "(unknown file)", 0, "(unknown function)", None

    while stacklevel > 0:
        next_f = f.f_back
        if next_f is None:
            break
        f = next_f
        stacklevel -= 1

    fname = f.f_code.co_filename
    fname = fname.replace(os.getcwd() + os.path.sep, "")
    funcname = f.f_code.co_name + "()"

    return fname, f.f_lineno, funcname

def _shorten(conf, msg):
    # shorten too long messages
    half = int(conf.max_length/2)
    if len(msg) > 2 * half:
        msg = msg[:half] + " ... " + msg[-half:]
    return msg.strip()

def _indent(conf, msg, i=0):
    # Wrap and indent a text by the same amount
    # as the lenght of 'CRITICAL'. If i=0, the first
    # line will not be indented.
    indent = " " * (len(_prefixes[FATAL]) + 2)
    wrapper = textwrap.TextWrapper(width=conf.line_width,
                                   initial_indent = indent * i,
                                   subsequent_indent = indent)
    return wrapper.fill(msg.strip())
