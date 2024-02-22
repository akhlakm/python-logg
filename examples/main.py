import module

import pylogg as log


def mainfn():
    log.fatal("Hello world")
    log.error("Hello world")
    log.warn("Hello world " * 200)
    log.note("Hello world")
    log.done("Hello world")
    log.info("Hello world")
    log.trace("Hello world")
    log.debug("Hello world")
    module.run()

def callback(msg : str):
    print("CB:", msg)

log.setFile(open('example.log', 'w+'))
log.setConsoleTimes(show=True)
log.setLevel(log.Level.DEBUG)

# Override the level of a named sub-logger.
log.setLoggerLevel('module', log.Level.INFO)


s = log.info("Staring main --", id=23)
mainfn()

log.setCallback(callback)
log.info("Test for callback")
log.setCallback(None)

s.done("main: {id}")
log.close()
