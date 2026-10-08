'''
This module provides an iterator over an archive containing other archives, and combines the
required and tarutil modules so an application can simply iterator over the archive once,
having established the required modes first
'''

try:
  from .enums import ReqMode
  from .required import Required
  from .tarutil import ArchiveMixin
except ImportError:
  from enums import ReqMode
  from required import Required
  from tarutil import ArchiveMixin

class ArchiveIter(ArchiveMixin):
  def __init__(self, archname: str, required: Required):
    ArchiveMixin.__init__(self, archname)
    self._reqd = required

  def __iter__(self):
    self.curmap = None
    return self

  def __next__(self):
    while True:
      tinfo = ArchiveMixin.next()
      mode = self._reqd.get(self.curmap, tinfo)
