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

t1 = log.init(log.Level.DEBUG)

# Override the level of a named sub-logger.
log.setLoggerLevel('module', log.Level.INFO)

log.info("Staring main --")
mainfn()

t1.done("main")
log.close()
