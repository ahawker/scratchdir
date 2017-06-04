import os, scratchdir

path = None

with scratchdir.ScratchDir() as sd:
    tmp = sd.named(delete=False)
    path = tmp.name
    print('Path {} exists? {}'.format(path, os.path.exists(path)))

print('Path {} exists? {}'.format(path, os.path.exists(path)))
