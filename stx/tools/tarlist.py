'''
This program will list all the members within a tar archive which can include other archives
'''

import collections
import dataclasses
import tarfile

def vers1():
  # Class representing a entry in the archive FIFO
  @dataclasses.dataclass
  class TarInfo:
    tarfd: tarfile.TarFile            # Archive file
    tinfo: tarfile.TarInfo = None     # Current member within archive
    reqd: bool = False                # Set if members are required
  
  # Class representing a archive with subarchives
  class TarList:
    def __init__(self, tarname):
      self._curr = TarInfo(tarfile.open(name=tarname, mode='r|*'))
      self._fifo = collections.deque()
  
    def push(self, tinfo):
      if tinfo.size:
        self._fifo.append(self._curr)
        self._curr = TarInfo(tarfile.open(fileobj=self._curr.tarfd.extractfile(self._curr.tinfo), mode='r|*'))
  
    def pop(self):
      self._curr = self._fifo.pop()
  
    def __iter__(self):
      return self
  
    def __next__(self):
      try:
        tinfo = self._curr.tarfd.next()
        while tinfo is None:
          self.pop()
          tinfo = self._curr.tarfd.next()
        self._curr.tinfo = tinfo
        if tinfo and tinfo.isreg() and tinfo.name.endswith(('.tar', '.tbz', 'txz')):
          self.push(tinfo)
        return tinfo
      except IndexError:
        raise StopIteration

  for ti in TarList('1404002s.tar'):
    print(ti.name)
  
def vers2():
  # Version making use of the tarutil.Archive class instead
  try:
    from . import tarutil
  except ImportError:
    import tarutil
  class TarList2(tarutil.Archive):
    def get_mode(self, tinfo):
      if tinfo.name.endswith(('.tar', '.tbz', '.txz')):
        return tarutil.ReqMode.PROCESS
      elif tinfo.isdir():
        return tarutil.ReqMode.SKIP
      else:
        return tarutil.ReqMode.NAMES

  architer = iter(TarList2('14040002s.tar'))
  for tinfo, data in architer:
    if data is None:
      match tinfo.name:
        case 'utool.txz':
          for tinfo, data in architer:
            int('UTOOL:', tinfo.name)
        case '
  for ti, fd in TarList2('1404002s.tar'):
    if fd is None:
      # New sub-archive encountered
      print('SUB -->', ti.name)
    elif isinstance(fd, str):
      # Owning archive or subarchive
      print(fd, '-->', ti.name)
    else:
      # File object of data
      print('DAT -->', ti.name)

if __name__ == '__main__':
  import sys
  if sys.argv[1] == '-1':
    vers1()
  elif sys.argv[1] == '-2':
    vers2()
  else:
    print('Pass -N to select version N to use')
