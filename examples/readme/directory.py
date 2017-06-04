import scratchdir

with scratchdir.ScratchDir() as sd:
    subdir = sd.directory()
    print(subdir)
