# Python-PyLogg
A personally opinionated logging package in Python.

Features:
- Colors in console.
- Saving log messages into a single file.
- Support for named sub-loggers.
- Override of log levels and settings from the main function.
- Eight levels of verbosity.
- Wrapping and shortening of long messages.
- Automatic logging of elapsed times for long processes.

## Installation
You can install this package from PyPI with `pip`.

```sh
pip install -U pylogg
```

## Usage
Set up the logger in the main script.

```python
import pylogg

pylogg.init(pylogg.Level.TRACE, colored=False)
pylogg.info("Hello world.")
```

Update individual settings if needed. These settings will override the settings set using `pylogg.get()` instances.

```python
import pylogg as log

# Set output file
log.setFile(open("test.log", "w+"))

# Show date and times on console
log.setConsoleTimes(show=True)

# Save date and times to file
log.setFileTimes(show=True)

# Set global logging level
log.setLevel(log.DEBUG)

# Override the level of a named sub-logger
log.setLoggerLevel('module', log.INFO)

# Use
log.info("Hello world")

# Close the log file
log.close()
```

Use sub-logger from the modules.
```python
import time
import pylogg

# Create or get a named sub-logger.
log = pylogg.get(__name__)

# Use
def run():
    log.Trace("Running module ...")

    # Support for f strings.
    log.Debug("2 + 2 = {} ({answer})", 2 + 2, answer=True)


def timing():
    # Get the timer instance
    t1 = log.Info("Started process ...")

    # long process
    time.sleep(2)

    # Call timer.done() to log elapsed time.
    t1.done("Process completed.")

```

**Note:** Full logg package must be imported. Use `import pylogg`,
do not use `from pylogg import get`.

See the [examples](https://github.com/akhlakm/python-logg/tree/main/examples)
for more details.

## Development
```sh
# Create a fork and clone the git repo.
git clone https://github.com/akhlakm/python-logg.git
cd python-logg

# Install dev requirements.
pip install -e .[dev]

# Install pre-commit git hooks.
pre-commit install

# Make changes and commit.

# Publish new tag.
./make.sh publish
```

## About
LICENSE MIT Copyright 2023 Akhlak Mahmood
