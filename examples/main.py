import pylogg as log
import module

def mainfn():
    log.Fatal("Hello world")
    log.Error("Hello world")
    log.Warn("Hello world " * 200)
    log.Note("Hello world")
    log.Done("Hello world")
    log.Info("Hello world")
    log.Trace("Hello world")
    log.Debug("Hello world")
    module.run()

log.SetFile(open('test.log', 'w+'))
# log.SetConsoleTimes(show=True)

s = log.Info("Staring main --", id=23)
mainfn()
s.Done("main: {id}")
log.Close()
