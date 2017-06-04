import scratchdir

with scratchdir.ScratchDir(prefix='grandparent-') as grandparent:
    print(grandparent.wd)
    with grandparent.child(prefix='parent-') as parent:
        print(parent.wd)
        with parent.child(prefix='child-') as child:
            print(child.wd)
