import pylogg

log = pylogg.New("module")

def run():
    log.Fatal("Hello world")
    log.Error("Hello world")
    log.Warn("Hello world " * 200)
    log.Note("Hello world")
    log.Done("Hello world")
    log.Info("Hello world")
    log.Trace("Hello world")
    log.Debug("Hello world")
