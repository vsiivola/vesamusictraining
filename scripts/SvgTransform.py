#!/usr/bin/env python

import xml.dom.minidom, subprocess, sys

class SvgTransform:
  def __init__(self, xml=None):
    self.xml = xml
    self.fname = None

  @classmethod 
  def get_bounds(cls, fname):
    cmd = ["/usr/bin/inkscape", "--without-gui", "--query-all", fname]
    #print (' '.join(cmd))
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    minx = 1000
    maxx = 0
    miny = 1000
    maxy = 0
    for line in proc.stdout:
      pname, a, b, c, d = line.decode('utf-8').split(',')
      x = float(a)
      y = float(b)
      width = float(c)
      height = float(d)
      if x<minx: 
        minx=x
      if x+width>maxx:
        maxx=x+width
      if y<miny: 
        miny=y
      if y+height>maxy:
        maxy=y+height
    return minx/6.5, miny/6.5, maxx/5.9, maxy/5.9
      
  @classmethod
  def init_from_file(cls, fname):
    sys.stderr.write("Read from '%s'\n" % fname)
    xmldoc = xml.dom.minidom.parse(fname)
    c = cls(xmldoc)
    c.minx, c.miny, c.maxx, c.maxy = cls.get_bounds(fname)
    return c
    
  def crop(self):
    doce = self.xml.getElementsByTagName("svg")[0]
    minx, miny, maxx, maxy = doce.getAttribute("viewBox").split()
    width = float(doce.getAttribute("width")[:-2]) # remove "mm"
    height = float(doce.getAttribute("height")[:-2])
    minx = float(minx)
    miny = float(miny)
    maxx = float(maxx)
    maxy = float(maxy)
    restuple = (minx+self.minx, miny+self.miny, self.maxx-self.minx, self.maxy-self.miny)
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

if __name__=="__main__":
  st = SvgTransform.init_from_file("work/tmp.svg")
  st.crop()
  st.write("work/tmp-mod.svg")


