import pylogg

# Log level 3 (warn) is set by the module.
log = pylogg.New("module").level(3)

def run():
    log.fatal("Hello world")
    log.error("Hello world")
    log.warning("Hello world " * 200)
    log.note("Hello world")
    log.done("Hello world")
    log.info("Hello world")
    log.trace("Hello world")
    log.debug("Hello world")
