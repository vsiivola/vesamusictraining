#!/usr/bin/env python

import os
import subprocess
import xml.dom.minidom

class SvgTransform:
    def __init__(self, xml=None, inkscape_path="/usr/bin"):
        self.xml = xml
        self.fname = None
        self.minx = None
        self.miny = None
        self.maxx = None
        self.maxy = None
        self.inkscape_bin = os.path.join(inkscape_path, "inkscape")

    def get_bounds(self, fname):
        cmd = [self.inkscape_bin, "--without-gui", "--query-all", fname]
        #print (' '.join(cmd))
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        minx = 1000
        maxx = 0
        miny = 1000
        maxy = 0
        for line in proc.stdout:
            _, a, b, c, d = line.decode('utf-8').split(',')
            x = float(a)
            y = float(b)
            width = float(c)
            height = float(d)
            if x < minx:
                minx = x
            if x+width > maxx:
                maxx = x+width
            if y < miny:
                miny = y
            if y + height > maxy:
                maxy = y + height
        return minx/6.5, miny/6.5, maxx/5.9, maxy/5.9

    @classmethod
    def init_from_file(cls, fname, inkscape_path="/opt/bin"):
        xmldoc = xml.dom.minidom.parse(fname)
        c = cls(xmldoc, inkscape_path)
        c.minx, c.miny, c.maxx, c.maxy = c.get_bounds(fname)
        return c

    def crop(self):
        doce = self.xml.getElementsByTagName("svg")[0]
        minx, miny, maxx, maxy = doce.getAttribute("viewBox").split()
        #width = float(doce.getAttribute("width")[:-2]) # remove "mm"
        #height = float(doce.getAttribute("height")[:-2])
        minx = float(minx)
        miny = float(miny)
        maxx = float(maxx)
        maxy = float(maxy)
        restuple = (minx+self.minx, miny+self.miny,
                    self.maxx-self.minx, self.maxy-self.miny)
        #print (st.minx, st.miny, st.maxx, st.maxy)
        #print (minx, miny, maxx, maxy)
        #print restuple
        doce.setAttribute("viewBox", "%.2f %.2f %.2f %.2f" % restuple)
        doce.setAttribute("width", "%.2f"% (6.5*(self.maxx-self.minx)))
        doce.setAttribute("height", "%.2f"% (6.5*(self.maxy-self.miny)))

    def write(self, fname):
        fout = open(fname, "w")
        fout.write(self.xml.toprettyxml())
        fout.close()

if __name__ == "__main__":
    st = SvgTransform.init_from_file("work/tmp.svg")
    st.crop()
    st.write("work/tmp-mod.svg")

