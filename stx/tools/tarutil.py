'''
This module provides access to a tar archive which can contain other archives within it,
this will handle any number of embedded archives.

Members that to made available as a file object are added to an instance of Required,
and then passed to initialiser of the Archive class togeather with the name of the
overall archive.

'''

import collections
import dataclasses
import tarfile
try:
  from .enums import ReqMode
except ImportError:
  from enums import ReqMode

__all__ = ('Archive',)

# Define the default list of archive extension which will trigger a subarchive action
_subarchive = (
  '.tar',
  '.tar.bz2', '.tbz', '.tbz2',
  '.tar.xz', '.txz',
  '.tar.zstd', '.tzstd',
)

@dataclasses.dataclass
class ArchInfo:
  'Class used internally to handle nesting of archives'
  fd: tarfile.TarFile
  name: str
  info: tarfile.TarInfo
  
  def is_archive(self):
    'Return whether member is a subarchive'
    return self.name in _subarchive

  def open(self):
    'Return an instance of fileobj for member'
    return self.fd.extractfile(self.info)  
    

class ArchiveMixin:
  '''Class providing the shared logic of handling an archive containing
     subarchives, resulting in each member in turn. This is meant to be
     used as a mixin to allow for the specific processing required by
     an application.
  '''
  def __init__(self, name: str) -> None:
    self.curr = ArchInfo(tarfile.open(name=name, mode='r|*'), name, None)
    self._fifo = collections.deque()

  def push(self, tinfo: ArchInfo | tarfile.TarInfo) -> None:
    ti = tinfo.info if isinstance(tinfo, ArchInfo) else tinfo
    if ti.size:
      newfd = tarfile.open(fileobj=self.curr.fd.extractfile(ti), mode='r|*')
      self._fifo.append(self.curr)
      self.curr = ArchInfo(newfd, ti.name, None)

  def pop(self) -> None:
    self.curr = self._fifo.pop()

  def next(self) -> ArchInfo:
    try:
      while self.curr:
        tinfo = self.curr.fd.next()
        while tinfo is None:
          self.pop()
          tinfo = self.curr.fd.next()
        self.curr.info = tinfo
        return self.curr
    except IndexError:
      raise StopIteration


class Archive(ArchiveMixin):
  '''Class which will iterate through the given tar archive, handling
     members according to the get_mode() which can be overridden to
     provide the correct handling for a particular module. Each call
     to the iterator will return a tuple which the following values and
     meanings:

       tinfo, None     - The given member is a new sub-archive, and can be
                         used to permit calling modules to know in which
                         sub-archive the member is in, and handles the case
                         where the first member of a sub-archive is itself
                         another sub-archive.
       tinfo, name     - The given member is part of the named subarchive/
       tinfo, fileobj  - The contents of the given member
  '''
  def __iter__(self) -> 'Archive':
    return self

  def __next__(self) -> ArchInfo | tuple[ArchInfo, tarfile.ExFileObject]:
    while True:
      ti = self.next()
      match self.is_mode(ti):
        case ReqMode.EXTRACT:
          # Extract the member and save on disk
          if hasattr(tarfile, 'tar_filter'):
            ti.fd.extract(ti.info, filter=tarfile.tar_filter)
          else:
            ti.fd.extract(ti.info)
          return ti
            
        case ReqMode.FILEOBJ:
          # Return an open file object with the name of the member
          return ti, ti.fd.extractfile(ti.info)
  
        case ReqMode.NAMES:
          # Return the member for further processing
          return ti
  
        case ReqMode.PROCESS:
          # Process the subarchive member
          self.push(ti)
          return ti
              
        case ReqMode.SKIP:
          # Skip the member and repeat loop
          pass
            
        case _:
          # Unhandled mode returned
          raise ValueError(f'Unhandled required mode')

  def is_mode(self, ti: ArchInfo) -> ReqMode:
    'Default handler for mode of member'
    if ti.info.isdir():
      return ReqMode.SKIP
    elif ti.info.name.endswith(_subarchive):
      return ReqMode.PROCESS
    else:
      return ReqMode.NAMES