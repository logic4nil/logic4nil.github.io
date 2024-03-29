#!/usr/bin/env python
# -*- encoding:utf8 -*-

import os

def tree(dirpath, level=0):
    dirs = {}
    files = {}
    for f in os.listdir(dirpath):
        fpath = "%s/%s" % (dirpath, f)
        if f.startswith("."):
            continue
        if os.path.isdir(fpath):
            dirs[f] = fpath
        elif fpath.endswith(".md"):
            files[f[:-3]] = fpath

    for d in sorted(dirs.items(), key=lambda d:d[0]):
        line = ""
        for i in range(level):
            line += " " * 3
        line += "* %s  " % (d[0], )
        print line
        tree(d[1], level+1)

    for f in sorted(files.items(), key=lambda d:d[0]):
        line = ""
        for i in range(level):
            line += " " * 3
        line +=  "* [%s](%s)  " % (f[0], f[1])
        print line


def main():
    print "# logic4nil"
    print "## 记录"
    tree(".")

    pass

if __name__ == "__main__":
    main()
