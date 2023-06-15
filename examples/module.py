import pylogg

log = pylogg.New("module")

def run():
    log.fatal("Hello world")
    log.error("Hello world")
    log.warning("Hello world " * 200)
    log.note("Hello world")
    log.done("Hello world")
    log.info("Hello world")
    log.trace("Hello world")
    log.debug("Hello world")
