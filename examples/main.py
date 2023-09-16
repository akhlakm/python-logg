import pylogg as log
import module

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

log.setFile(open('example.log', 'w+'))
log.setConsoleTimes(show=True)
log.setLevel(log.Level.DEBUG)

# Override the level of a named sub-logger.
log.setLoggerLevel('module', log.Level.INFO)


s = log.info("Staring main --", id=23)
mainfn()

s.done("main: {id}")
log.close()
