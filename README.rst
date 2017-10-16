scratchdir
==========

|Build Status| |codecov| |Code Climate| |Issue Count|

|PyPI Version| |PyPI Versions|

Context manager to maintain your temporary directories/files.

Installation
~~~~~~~~~~~~

To install scratchdir from `pip <https://pypi.python.org/pypi/pip>`__:

.. code:: bash

        $ pip install scratchdir

To install scratchdir from source:

.. code:: bash

        $ git clone git@github.com:ahawker/scratchdir.git
        $ python setup.py install

Usage
~~~~~

Creating a new ``ScratchDir`` is simple. Just instantiate a new instance
and call ``setup``:

.. code:: bash

    ⇒  cat examples/readme/setup.py
    import scratchdir

    sd = scratchdir.ScratchDir()
    sd.setup()
    print(sd.wd)
    sd.teardown()

    ⇒  python examples/readme/usage-1.py
    /var/folders/86/zhtx1pv53qs2mm1fq1k1841w0000gn/T/3e56r54m.scratchdir

Or as a context manager using the ``with`` statement:

.. code:: bash

    ⇒  cat examples/readme/context-manager.py
    import scratchdir

    with scratchdir.ScratchDir() as sd:
        print(sd.wd)

    ⇒  python examples/readme/context-manager.py
    /var/folders/86/zhtx1pv53qs2mm1fq1k1841w0000gn/T/_ibfhq1s.scratchdir

Files created by the ``ScratchDir`` are automatically cleaned up on
teardown:

::

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

Directories within the ``ScratchDir`` are also easy to create:

.. code:: bash

    ⇒  cat examples/readme/directory.py
    import scratchdir

    with scratchdir.ScratchDir() as sd:
        subdir = sd.directory()
        print(subdir)

    ⇒  python examples/readme/directory.py
    /var/folders/86/zhtx1pv53qs2mm1fq1k1841w0000gn/T/c1odkxbw.scratchdir/tmpcyeqjk1v

Methods on the ``ScratchDir`` instance will pass arguments down to their
corresponding functions in
`tempfile <https://docs.python.org/3.6/library/tempfile.html#module-tempfile>`__.

.. code:: bash

    ⇒  cat examples/readme/params.py
    import scratchdir

    with scratchdir.ScratchDir() as sd:
        tmp = sd.named(suffix='.txt', prefix='logfile-', delete=False)
        print(tmp.name)

    ⇒  python examples/readme/params.py
    /var/folders/86/zhtx1pv53qs2mm1fq1k1841w0000gn/T/1h_7379t.scratchdir/logfile-z1gq195q.txt

Creating a hierarchy of ``ScratchDir`` instances to match that of your
domain objects is also simple:

.. code:: bash

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

Methods
~~~~~~~

The ``ScratchDir`` instance maintains a set of bound methods are map to
functions/classes within the
`tempfile <https://docs.python.org/3.6/library/tempfile.html#module-tempfile>`__
module in the standard library. A table of methods is as follows:

+------+------+------+
| scra | temp | desc |
| tchd | file | ript |
| ir   |      | ion  |
+======+======+======+
| file | Temp | Crea |
| ,    | orar | te   |
| Temp | yFil | a    |
| orar | e    | name |
| yFil |      | less |
| e    |      | temp |
|      |      | orar |
|      |      | y    |
|      |      | file |
|      |      | that |
|      |      | is   |
|      |      | auto |
|      |      | mati |
|      |      | call |
|      |      | y    |
|      |      | dele |
|      |      | ted  |
|      |      | once |
|      |      | it's |
|      |      | clos |
|      |      | ed.  |
+------+------+------+
| name | Name | Crea |
| d,   | dTem | te   |
| Name | pora | a    |
| dTem | ryFi | temp |
| pora | le   | orar |
| ryFi |      | y    |
| le   |      | file |
|      |      | that |
|      |      | rece |
|      |      | ives |
|      |      | a    |
|      |      | file |
|      |      | name |
|      |      | on   |
|      |      | disk |
|      |      | that |
|      |      | is   |
|      |      | auto |
|      |      | mati |
|      |      | call |
|      |      | y    |
|      |      | dele |
|      |      | ted  |
|      |      | once |
|      |      | it's |
|      |      | clos |
|      |      | ed   |
|      |      | unle |
|      |      | ss   |
|      |      | the  |
|      |      | ``de |
|      |      | lete |
|      |      | ``   |
|      |      | para |
|      |      | mete |
|      |      | r    |
|      |      | is   |
|      |      | ``Fa |
|      |      | lse` |
|      |      | `.   |
+------+------+------+
| spoo | Spoo | Crea |
| led, | ledT | te   |
| Spoo | empo | a    |
| ledT | rary | temp |
| empo | File | orar |
| rary |      | y    |
| File |      | file |
|      |      | that |
|      |      | will |
|      |      | over |
|      |      | flow |
|      |      | from |
|      |      | memo |
|      |      | ry   |
|      |      | onto |
|      |      | disk |
|      |      | once |
|      |      | a    |
|      |      | defi |
|      |      | ned  |
|      |      | maxi |
|      |      | mum  |
|      |      | size |
|      |      | is   |
|      |      | exce |
|      |      | eded |
|      |      | .    |
+------+------+------+
| secu | mkst | Crea |
| re,  | emp  | te   |
| mkst |      | a    |
| emp  |      | temp |
|      |      | orar |
|      |      | y    |
|      |      | file |
|      |      | in   |
|      |      | as   |
|      |      | secu |
|      |      | re   |
|      |      | way  |
|      |      | as   |
|      |      | poss |
|      |      | ible |
|      |      | .    |
+------+------+------+
| dire | mkdt | Crea |
| ctor | emp  | te   |
| y,   |      | a    |
| mkdt |      | temp |
| emp  |      | orar |
|      |      | y    |
|      |      | dire |
|      |      | ctor |
|      |      | y.   |
+------+------+------+
| file | N/A  | Crea |
| name |      | te   |
|      |      | a    |
|      |      | uniq |
|      |      | ue   |
|      |      | file |
|      |      | name |
|      |      | with |
|      |      | in   |
|      |      | the  |
|      |      | ``Sc |
|      |      | ratc |
|      |      | hDir |
|      |      | ``.  |
+------+------+------+
| join | N/A  | Join |
|      |      | a    |
|      |      | numb |
|      |      | er   |
|      |      | of   |
|      |      | path |
|      |      | s    |
|      |      | to   |
|      |      | the  |
|      |      | root |
|      |      | of   |
|      |      | the  |
|      |      | ``Sc |
|      |      | ratc |
|      |      | hDir |
|      |      | ``.  |
+------+------+------+

Goals
~~~~~

I've implemented similar functionality three times now, starting with my
`scatter <https://github.com/ahawker/scatter>`__ project back in
2013-2014. I'd rather not write it *again*, so the goal is that
scratchdir should be generic and reusable for future projects.

Contributing
~~~~~~~~~~~~

If you would like to contribute, simply fork the repository, push your
changes and send a pull request.

License
~~~~~~~

Scratchdir is avaialble under the `Apache 2.0 <LICENSE>`__ license.

.. |Build Status| image:: https://travis-ci.org/ahawker/scratchdir.svg?branch=master
   :target: https://travis-ci.org/ahawker/scratchdir
.. |codecov| image:: https://codecov.io/gh/ahawker/scratchdir/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/ahawker/scratchdir
.. |Code Climate| image:: https://codeclimate.com/github/ahawker/scratchdir/badges/gpa.svg
   :target: https://codeclimate.com/github/ahawker/scratchdir
.. |Issue Count| image:: https://codeclimate.com/github/ahawker/scratchdir/badges/issue_count.svg
   :target: https://codeclimate.com/github/ahawker/scratchdir
.. |PyPI Version| image:: https://badge.fury.io/py/scratchdir.svg
   :target: https://badge.fury.io/py/scratchdir
.. |PyPI Versions| image:: https://img.shields.io/pypi/pyversions/scratchdir.svg
   :target: https://pypi.python.org/pypi/scratchdir
