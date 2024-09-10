"""
A personally opinionated logging package.
LICENSE MIT Copyright 2024 Akhlak Mahmood

"""

__version__ = "0.4.1"
__author__ = "Akhlak Mahmood"

import os
import sys
import textwrap
import time
from datetime import datetime, timezone


class Level:
    NONE  = 0
    FATAL = 1
    ERROR = 2
    WARN  = 3
    NOTE  = 4
    DONE  = 5
    INFO  = 6
    TRACE = 7
    DEBUG = 8

_prefixes = {
    Level.NONE:  "        ", # no prefix/level
    Level.FATAL: "CRITICAL", # process must exit
    Level.ERROR: "ERROR --", # irrecoverable error
    Level.WARN:  "WARN  --", # unexpected or rare condition
    Level.NOTE:  "NOTE  --", # special messages
    Level.DONE:  "  OK  --", # success message, progress reporting
    Level.INFO:  "      --", # info messages, verbose
    Level.TRACE: "  --  --", # start of something, 2x verbose
    Level.DEBUG: "DEBUG --", # for development
}

_reset_seq = "\033[0m"
_red, _green, _yellow, _blue, _magenta, _cyan, _white = range(31, 38)

_color_seqs = {
    Level.NONE:   "\033[0;%dm" % _green,
    Level.FATAL:  "\033[1;%dm" % _red,
    Level.ERROR:  "\033[1;%dm" % _yellow,
    Level.WARN:   "\033[0;%dm" % _magenta,
    Level.NOTE:   "\033[1;%dm" % _cyan,
    Level.DONE:   "\033[0;%dm" % _blue,
    Level.INFO:   "\033[1;%dm" % _cyan,
    Level.TRACE:  "\033[0;%dm" % _white,
    Level.DEBUG:  "\033[1;%dm" % _white,
}

class _config(object):
    logger = ""       # name of the logger
    level = Level.INFO      # cofigured log level
    max_length = 500  # maximum length of a formatted message
    file_times      = True      # show times or not
    console_times   = False     # show times or not
    console_stderr  = False     # print to stderr or stdout
    time_fmt = "%y-%m-%d %Z %I:%M:%S %p"
    color = True      # show colors or not
    fileh = None      # handle to a logfile
    file_stack = False     # save caller info to logfile or not
    console_stack = False  # show caller info on console or not
    line_width = 100    # fix width of the log messages
    callback : callable = None  # Additional function to send the log message
    _lastInfoTime = None # pvt var to measure execution time
    _init : bool = False # if log has been initialized

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

    def note(self, msg, *args, **kwargs):
        """ Log a note message for the task. """
        self._kwargs.update(kwargs)
        self._kwargs['time_elapsed'] = self.elapsed()
        _log(self._conf, Level.NOTE, _stack_info(), msg, *args, **self._kwargs)

    def done(self, msg, *args, **kwargs):
        """ Log a done message for the task. """
        self._kwargs.update(kwargs)
        self._kwargs['time_elapsed'] = self.elapsed()
        _log(self._conf, Level.DONE, _stack_info(), msg, *args, **self._kwargs)

    def info(self, msg, *args, **kwargs):
        """ Log an info message for the task. """
        self._kwargs.update(kwargs)
        self._kwargs['time_elapsed'] = self.elapsed()
        _log(self._conf, Level.INFO, _stack_info(), msg, *args, **self._kwargs)

    def warn(self, msg, *args, **kwargs):
        """ Log a warning for the task. """
        self._kwargs.update(kwargs)
        self._kwargs['time_elapsed'] = self.elapsed()
        _log(self._conf, Level.WARN, _stack_info(), msg, *args, **self._kwargs)

    def section(self, msg = "", sep = "-", linebreak = False, **kwargs):
        """ Log a warning for the task. """
        self._kwargs.update(kwargs)
        self._kwargs['time_elapsed'] = self.elapsed()
        section(msg, sep, linebreak, **self._kwargs)


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
        """ Update individual settings of the named logger. """
        avail = [v for v in vars(_config) if not v.startswith("_")]
        if key in avail:
            self.conf[key] = value
        else:
            raise AttributeError("Unknown setting: '%s'\nAvailable: %s" %(key, avail))
        return self

    def setLevel(self, level : int | Level):
        """ Override the level of this named logger. """
        return self.update('level', level)

    def set(self, key, value):
        """ Set individual settings of the named logger. """
        return self.update(key, value)

    def setCallback(self, cb: callable):
        """ Add a callback function to pass the formatted log messages.
            Set None to remove.
        """
        assert callable(cb) or cb is None, \
            "Callback must be a callable(str) or None"
        self.conf['callback'] = cb

    def _log(self, level, stack, msg, *args, **kwargs):
        # Update with the module level configurations,
        # in case it was changed after importing the named logger.
        self.__dict__.update(_conf.__dict__)

        # Override with sub-logger level configurations.
        self.__dict__.update(self.conf)
        _log(self, level, stack, msg, *args, **kwargs)

    def fatal(self, msg, *args, **kwargs):
        self._log(Level.FATAL, _stack_info(), msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        self._log(Level.FATAL, _stack_info(), msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self._log(Level.ERROR, _stack_info(), msg, *args, **kwargs)

    def warn(self, msg, *args, **kwargs):
        self._log(Level.WARN, _stack_info(), msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self._log(Level.WARN, _stack_info(), msg, *args, **kwargs)

    def note(self, msg, *args, **kwargs) -> Timer:
        self._log(Level.NOTE, _stack_info(), msg, *args, **kwargs)
        return Timer(self, **kwargs)

    def done(self, msg, *args, **kwargs):
        self._log(Level.DONE, _stack_info(), msg, *args, **kwargs)

    def section(self, msg = "", sep = "-", linebreak = True, **kwargs) -> Timer:
        return section(msg, sep, linebreak, **kwargs)

    def info(self, msg, *args, **kwargs) -> Timer:
        self._log(Level.INFO, _stack_info(), msg, *args, **kwargs)
        return Timer(self, **kwargs)

    def trace(self, msg, *args, **kwargs) -> Timer:
        self._log(Level.TRACE, _stack_info(), msg, *args, **kwargs)
        return Timer(self, **kwargs)

    def debug(self, msg, *args, **kwargs):
        self._log(Level.DEBUG, _stack_info(), msg, *args, **kwargs)


def New(name) -> _new:
    """
    Get the logger with name or create a new named logger.
    """
    if not name in _manager:
        log = _new(name)
        _manager[name] = log
    return _manager[name]

def get(name) -> _new:
    """
    Get the logger with name or create a new named logger.
    """
    return New(name)

def _colorize(conf, level, msg):
    if not conf.color:
        return msg
    else:
        return f"{_color_seqs[level]}{msg}{_reset_seq}"

def _save(conf : _config, level, fmtmsg, timestr, caller):
    """ Log to file or callback """

    if not conf.file_times:
        timestr = ""

    extra = ""
    if conf.file_stack or level in [Level.FATAL, Level.ERROR, Level.DEBUG]:
        extra += caller

    # Allow spacings
    if len(fmtmsg.strip()) and level > Level.NONE:
        prefix = _prefixes[level]
        fmtlogger = f"{conf.logger}_ " if conf.logger else ""
        line = f"{timestr}{prefix} {fmtlogger}{fmtmsg} {extra}"
        line = _indent(conf, line)
    else:
        line = fmtmsg

    if conf.fileh:
        conf.fileh.write(line + "\n")
        conf.fileh.flush()
        os.fsync(conf.fileh.fileno())

    if conf.callback:
        try:
            conf.callback(line)
        except Exception as err:
            print(err)

    return line


def _print(conf : _config, level, fmtmsg, timestr, caller):
    if not conf.console_times:
        timestr = ""

    extra = ""
    if conf.console_stack or level in [Level.FATAL, Level.ERROR, Level.DEBUG]:
        extra += caller

    # Allow spacings
    if len(fmtmsg.strip()) and level > Level.NONE:
        prefix = _colorize(conf, level, _prefixes[level])
        if level in [Level.FATAL, Level.ERROR, Level.DEBUG]:
            fmtmsg = _colorize(conf, level, fmtmsg)

        fmtlogger = f"{conf.logger}_ " if conf.logger else ""
        line = f"{timestr}{prefix} {fmtlogger}{fmtmsg} {extra}"
        line = _indent(conf, line)
    else:
        line = _colorize(conf, level, fmtmsg)

    if conf.console_stderr:
        print(line, file=sys.stderr, flush=True)
    else:
        print(line, file=sys.stdout, flush=True)
    return line

def _log(conf : _config, level : int, stack : tuple, msg : str, *args, **kwargs):
    # changed in v0.3.4: use the level set to the named log, not the global level
    max_level = _levelOverrides[conf.logger] if conf.logger in _levelOverrides else conf.level

    if max_level < level:
        return

    # Caller info
    lineno = stack[1]
    funcname = stack[2]
    filepath = stack[0]
    caller = f"[{funcname} {filepath}:{lineno}]"

    # Date time info
    local_now = datetime.now(timezone.utc).astimezone()
    timestr = local_now.strftime(f"[{_conf.time_fmt}]") + " "

    if "{" in msg and "}" in msg:
        # info("Hello {}", "world")
        try:
            fmtmsg = msg.format(*args, **kwargs)
        except:
            fmtmsg = msg
    else:
        # info("Hello", "world")
        fmtmsg = " ".join([msg] + [str(s) for s in args])

    # Allow spacings
    if len(fmtmsg.strip()):
        fmtmsg = _shorten(conf, fmtmsg, level)

    # Timer info
    if 'time_elapsed' in kwargs:
        fmtmsg = f"{fmtmsg} (took {kwargs['time_elapsed']:.3f} s)"

    _print(conf, level, fmtmsg, timestr, caller)
    _save(conf, level, fmtmsg, timestr, caller)


def fatal(msg, *args, **kwargs):
    _log(_conf, Level.FATAL, _stack_info(), msg, *args, **kwargs)

def critical(msg, *args, **kwargs):
    _log(_conf, Level.FATAL, _stack_info(), msg, *args, **kwargs)

def error(msg, *args, **kwargs):
    _log(_conf, Level.ERROR, _stack_info(), msg, *args, **kwargs)

def warn(msg, *args, **kwargs):
    _log(_conf, Level.WARN, _stack_info(), msg, *args, **kwargs)

def warning(msg, *args, **kwargs):
    _log(_conf, Level.WARN, _stack_info(), msg, *args, **kwargs)

def note(msg, *args, **kwargs) -> Timer:
    _log(_conf, Level.NOTE, _stack_info(), msg, *args, **kwargs)
    return Timer(_conf, **kwargs)

def done(msg, *args, **kwargs):
    _log(_conf, Level.DONE, _stack_info(), msg, *args, **kwargs)

def info(msg, *args, **kwargs) -> Timer:
    _log(_conf, Level.INFO, _stack_info(), msg, *args, **kwargs)
    return Timer(_conf, **kwargs)

def trace(msg, *args, **kwargs) -> Timer:
    _log(_conf, Level.TRACE, _stack_info(), msg, *args, **kwargs)
    return Timer(_conf, **kwargs)

def debug(msg, *args, **kwargs):
    _log(_conf, Level.DEBUG, _stack_info(), msg, *args, **kwargs)

def section(msg = "", sep = '-', linebreak = True, **kwargs):
    msg = msg if len(msg) else kwargs.get('section', msg)
    width = (_conf.line_width - len(msg)) // 2
    if len(msg):
        kwargs['section'] = msg
        msg = " ".join([sep * width, msg, sep * width])
    else:
        msg = sep * (2 * width + 2)

    if linebreak:
        # Add a linebreak
        _log(_conf, Level.NONE, _stack_info(), '')

    _log(_conf, Level.NONE, _stack_info(), msg)
    return Timer(_conf, **kwargs)

def close(msg = "~", level = Level.DONE):
    """ Shutdown logging. Close any open handles. """
    _log(_conf, level, _stack_info(), "~")
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

def setColor(*, show : bool = True):
    """ Enable or disable colored logging to console.
    """
    _conf.color = show

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

def setConsoleOutput(*, stderr : bool = None):
    """
    Output console logs to stderr or not.
    Default output is stdout.
    """
    if stderr:
        _conf.console_stderr = True

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

def setCallback(cb: callable):
    """ Add a callback function to pass the formatted log messages.
        Set None to remove.
    """
    assert callable(cb) or cb is None, \
        "Callback must be a callable(str) or None"
    _conf.callback = cb


def init(log_level : int = Level.DONE, output_directory : str = "logs",
            logfile_name : str = None, colored = True, console_times = False,
            append_to_logfile : bool = False):
    """
        Intialize a logger and logfile to a specific directory.

        log_level:          The log level (1-8), higher is more verbose.
        output_directory:   The directory to save the logfile.
        logfile_name:       The name of the logfile (default: python file name).
        colored:            Use colors on console.
        console_times:      Show timestamp on console.
        append_to_logfile:  Append logfile instead of overwriting.

        Returns a log Timer.

    """
    # close previous log files.
    if _conf._init:
        close()

    script_name = os.path.splitext(os.path.basename(sys.argv[0]))[0]
    if logfile_name is None:
        logfile_name = f"{script_name}.log"

    logfile_path = os.path.join(output_directory, logfile_name)
    os.makedirs(os.path.dirname(logfile_path), exist_ok=True)

    if append_to_logfile:
        log_file = open(logfile_path, "a+")
    else:
        # Rotate existing log file if not appending.
        if os.path.isfile(logfile_path):
            rotated = _calc_file_rotation(logfile_path)
            os.rename(logfile_path, rotated)

        log_file = open(logfile_path, "w+")

    os.chmod(logfile_path, 0o600)
    _printstderr(f"Logging to file: {logfile_path}\n")

    setFile(log_file)
    setLevel(log_level)
    setColor(show=colored)
    setFileTimes(show=True)
    setConsoleTimes(show=console_times)

    _conf._init = True
    log_level_name = [k for k, v in Level.__dict__.items() if v == log_level][0]
    log_info = f"{log_level_name} (v{__version__})"

    section(script_name, linebreak=False)
    note("Loglevel: {}", log_info)
    note("Args: {}", " ".join(sys.argv))
    note("CWD: {}", os.getcwd())
    note("Host: {}", os.uname().nodename)
    note("Logfile: {}", logfile_path)
    return section(linebreak=False)


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

def _shorten(conf, msg, level):
    if level < Level.WARN:
        return msg.strip()
    else:
        # shorten too long messages
        half = int(conf.max_length/2)
        if len(msg) > 2 * half:
            msg = msg[:half] + " ... " + msg[-half:]
        return msg.strip()

def _indent(conf, msg, i=0):
    # Wrap and indent a text by the same amount
    # as the lenght of 'CRITICAL'. If i=0, the first
    # line will not be indented.
    indent = " " * (len(_prefixes[Level.FATAL]) + 2)
    wrapper = textwrap.TextWrapper(width=conf.line_width,
                                   initial_indent = indent * i,
                                   subsequent_indent = indent)
    return wrapper.fill(msg)


def _calc_file_rotation(filepath) -> str:
    # Return a new file name by adding a suffix with a serial number
    # before the extension.
    path, ext = os.path.splitext(filepath)
    for i in range(1, 10000):
        fname = f"{path}.{i:02d}{ext}"
        if not os.path.isfile(fname):
            return fname
    raise RuntimeError("Cannot rotate logfile, too may files found.")

def _printstderr(message):
    print(message, file=sys.stderr, flush=True)
