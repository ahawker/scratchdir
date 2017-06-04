import scratchdir

with scratchdir.ScratchDir() as sd:
    tmp = sd.named(suffix='.txt', prefix='logfile-', delete=False)
    print(tmp.name)
