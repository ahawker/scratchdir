# scratchdir

[![Build Status](https://travis-ci.org/ahawker/scratchdir.svg?branch=master)](https://travis-ci.org/ahawker/scratchdir)
[![codecov](https://codecov.io/gh/ahawker/scratchdir/branch/master/graph/badge.svg)](https://codecov.io/gh/ahawker/scratchdir)
[![Code Climate](https://codeclimate.com/github/ahawker/scratchdir/badges/gpa.svg)](https://codeclimate.com/github/ahawker/scratchdir)
[![Issue Count](https://codeclimate.com/github/ahawker/scratchdir/badges/issue_count.svg)](https://codeclimate.com/github/ahawker/scratchdir)

[![PyPI Version](https://badge.fury.io/py/scratchdir.svg)](https://badge.fury.io/py/scratchdir)
[![PyPI Versions](https://img.shields.io/pypi/pyversions/scratchdir.svg)](https://pypi.python.org/pypi/scratchdir)

Context manager to maintain your temporary directories/files.

### Installation
To install scratchdir from [pip](https://pypi.python.org/pypi/pip):
```bash
    $ pip install scratchdir
```

To install scratchdir from source:
```bash
    $ git clone git@github.com:ahawker/scratchdir.git
    $ python setup.py install
```

### Usage

Creating a new `ScratchDir` is simple. Just instantiate a new instance and call `setup`:
```bash
⇒  cat examples/readme/setup.py
import scratchdir

sd = scratchdir.ScratchDir()
sd.setup()
print(sd.wd)
sd.teardown()

⇒  python examples/readme/usage-1.py
/var/folders/86/zhtx1pv53qs2mm1fq1k1841w0000gn/T/3e56r54m.scratchdir
```

Or as a context manager using the `with` statement:
```bash
⇒  cat examples/readme/context-manager.py
import scratchdir

with scratchdir.ScratchDir() as sd:
    print(sd.wd)

⇒  python examples/readme/context-manager.py
/var/folders/86/zhtx1pv53qs2mm1fq1k1841w0000gn/T/_ibfhq1s.scratchdir
```

Files created by the `ScratchDir` are automatically cleaned up on teardown:
```
⇒  cat examples/readme/cleanup.py
import os
import scratchdir

path = None

with scratchdir.ScratchDir() as sd:
    tmp = sd.named(delete=False)
    path = tmp.name
    print('Path {} exists? {}'.format(path, os.path.exists(path)))

print('Path {} exists? {}'.format(path, os.path.exists(path)))

⇒  python examples/readme/cleanup.py
Path /var/folders/86/zhtx1pv53qs2mm1fq1k1841w0000gn/T/y1aedyk8.scratchdir/tmp7m79rev1 exists? True
Path /var/folders/86/zhtx1pv53qs2mm1fq1k1841w0000gn/T/y1aedyk8.scratchdir/tmp7m79rev1 exists? False
```

Directories within the `ScratchDir` are also easy to create:

```bash
⇒  cat examples/readme/directory.py
import scratchdir

with scratchdir.ScratchDir() as sd:
    subdir = sd.directory()
    print(subdir)

⇒  python examples/readme/directory.py
/var/folders/86/zhtx1pv53qs2mm1fq1k1841w0000gn/T/c1odkxbw.scratchdir/tmpcyeqjk1v
```

Methods on the `ScratchDir` instance will pass arguments down to their corresponding functions in [tempfile](https://docs.python.org/3.6/library/tempfile.html#module-tempfile).

```bash
⇒  cat examples/readme/params.py
import scratchdir

with scratchdir.ScratchDir() as sd:
    tmp = sd.named(suffix='.txt', prefix='logfile-', delete=False)
    print(tmp.name)

⇒  python examples/readme/params.py
/var/folders/86/zhtx1pv53qs2mm1fq1k1841w0000gn/T/1h_7379t.scratchdir/logfile-z1gq195q.txt
```

Creating a hierarchy of `ScratchDir` instances to match that of your domain objects is also simple:

```bash
⇒  cat examples/readme/hierarchy.py
import scratchdir

with scratchdir.ScratchDir(prefix='grandparent-') as grandparent:
    print(grandparent.wd)
    with grandparent.child(prefix='parent-') as parent:
        print(parent.wd)
        with parent.child(prefix='child-') as child:
            print(child.wd)

⇒  python examples/readme/hierarchy.py
/var/folders/86/zhtx1pv53qs2mm1fq1k1841w0000gn/T/grandparent-4ld_pl8f.scratchdir
/var/folders/86/zhtx1pv53qs2mm1fq1k1841w0000gn/T/grandparent-4ld_pl8f.scratchdir/parent-s6y_gmxg.scratchdir
/var/folders/86/zhtx1pv53qs2mm1fq1k1841w0000gn/T/grandparent-4ld_pl8f.scratchdir/parent-s6y_gmxg.scratchdir/child-28k2hpdk.scratchdir
```

### Methods
The `ScratchDir` instance maintains a set of bound methods are map to functions/classes within the [tempfile](https://docs.python.org/3.6/library/tempfile.html#module-tempfile)
module in the standard library. A table of methods is as follows:

| scratchdir | tempfile | description
| --- | --- | --- |
| file, TemporaryFile | TemporaryFile | Create a nameless temporary file that is automatically deleted once it's closed.
| named, NamedTemporaryFile | NamedTemporaryFile | Create a temporary file that receives a filename on disk that is automatically deleted once it's closed unless the `delete` parameter is `False`.
| spooled, SpooledTemporaryFile | SpooledTemporaryFile | Create a temporary file that will overflow from memory onto disk once a defined maximum size is exceeded.
| secure, mkstemp | mkstemp | Create a temporary file in as secure way as possible.
| directory, mkdtemp | mkdtemp | Create a temporary directory.
| filename | N/A | Create a unique filename within the `ScratchDir`.
| join | N/A | Join a number of paths to the root of the `ScratchDir`.

### Goals
I've implemented similar functionality three times now, starting with my [scatter](https://github.com/ahawker/scatter) project back in 2013-2014.
I'd rather not write it _again_, so the goal is that scratchdir should be generic and reusable for future projects.

### Contributing
If you would like to contribute, simply fork the repository, push your changes and send a pull request.

### License
Scratchdir is avaialble under the [Apache 2.0](LICENSE) license.
