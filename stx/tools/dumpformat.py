'''
Dump the possible values for the formats showing the possible flags per field type.

Only the UK language formats will be processed, no user tailored or transient tables are handled either.
'''

import collections
import os.path
import tarfile
from dataclasses import dataclass
try:
  from .textutil import UnpackError, unpack, unpack_dict
except ImportError:
  from textutil import UnpackError, unpack, unpack_dict

# Iterator to travers the development image to return the member containing the format information
@dataclass
class FormatArchiveInfo:
  tarfd: tarfile.TarFile
  tinfo: tarfile.TarInfo = None
  reqd: bool = False

class FormatArchive:
  def __init__(self, tarname, lang='uk'):
    self._curr = FormatArchiveInfo(tarfile.open(name=tarname, mode='r|'))
    self._fifo = collections.deque()
    self._reqd = (f'format/{lang}.txz',)

  def push_archive(self, tinfo):
    try:
      tarfd = tarfile.open(fileobj=self._curr.tarfd.extractfile(self._curr.tinfo), mode='r|xz')
    except tarfile.CompressionError:
      return
    if self._curr is not None:
      self._fifo.append(self._curr)
    self._curr = FormatArchiveInfo(tarfd)

  def pop_archive(self):
    if self._curr is not None:
      self._curr.tarfd.close()
    self._curr = self._fifo.pop()

  def __iter__(self):
    return self

  def __next__(self):
    try:
      while self._curr:
        tinfo = self._curr.tarfd.next()
        while tinfo is None:
          self.pop_archive()
          tinfo = self._curr.tarfd.next()
        self._curr.tinfo = tinfo
        if tinfo and tinfo.name in self._reqd:
          self.push_archive(tinfo)
          self._curr.reqd = True
          continue
        elif self._curr.reqd:
          return tinfo
    except IndexError:
      raise StopIteration

  def open(self):
    return self._curr.tarfd.extractfile(self._curr.tinfo)

# Flag information for each type of field
class FieldInfo:
  def __init__(self):
    self.standout = set()
    self.inpmode = set()
    self.signed = set()
    self.zeros = set()
    self.typlzero = set()
    self.convert = set()
    self.showhelp = set()
    self.wholenum = set()
    self.deftyp = set()

  def update(self, flddict):
    self.standout.add(flddict.standout)
    self.inpmode.add(flddict.inmode)
    self.signed.add(flddict.signed)
    self.zeros.add(flddict.zeros)
    self.typlzero.add(flddict.typlzero)
    self.convert.add(flddict.convert)
    self.showhelp.add(flddict.showhelp)
    self.wholenum.add(flddict.wholenum)
    self.deftyp.add(flddict.deftyp)

# Flag information for all formats
class FormatInfo:
  clear = set()
  rsense = set()
  repeat = set()
  confirm = set()
  standout = set()
  overlap = set()
  fldtype = dict()

  def update(self, fmtdict):
    self.clear.add(fmtdict.clear)
    self.rsense.add(fmtdict.rsense)
    self.repeat.add(fmtdict.repeat)
    self.confirm.add(fmtdict.confirm)
    self.standout.add(fmtdict.standout)
    self.overlap.add(fmtdict.overlap)

  def add_field(self, flddict):
    elem = self.fldtype.get(flddict.fldtype, None)
    if elem is None:
      elem = self.fldtype[flddict.fldtype] = FieldInfo()
    elem.update(flddict)

def parse_format(fd, flags):
  # Process the header line
  flags.update(unpack_dict('{3d:hpos}{3d:vpos}{3d:width}{3d:depth}{c:clear}{3d:repeat}{4c:rsense;confirm;standout;overlap}', fd))
  # Process fields until an empty line is encountered or end of file
  data = fd.readline()
  while data and data != b'\n':
    # Process field information
    field = unpack_dict('{9s:fldname}#{7*}{d:numhelp}{c:fldtype}{2d:numdec}{3d:fidsize}{3d:strsize}{c:strtype}{3d:hpos}{3d:vpos}{2c:standout;inmode}'
                        '{10s:valtab}{5c:signed;zeros;typlzero;convert;showhelp}{10s:fldgroup}{10s:defval}{c:wholenum}{2*}{3d:pmtseq}{c:deftyp}', data)
    # Skip help text
    for n in range(field.numhelp):
      fd.readline()
    # Populate the appropriate information for the field type
    flags.add_field(field)
    # Read next field
    data = fd.readline()

def main(dbname='uk_format.db'):
  tfpath = f'{os.path.dirname(__file__)}/1404002.tar'
  tf = FormatArchive(tfpath, 'uk')
  fi = FormatInfo()
  for ti in iter(tf):
    if ti.size > 10:
      # Process all new screen entities
      entname = os.path.basename(ti.name)
      with tf.open() as fd:
        try:
          if unpack('010105%c', fd)[0].isdigit():
            parse_format(fd, fi)
        except UnpackError:
          pass

  print('FORMAT:')
  print('  clear:', fi.clear)
  print('  rsense:', fi.rsense)
  print('  repeat:', fi.repeat)
  print('  confirm:', fi.confirm)
  print('  standout:', fi.standout)
  print('  overlap:', fi.overlap)
  comb = FieldInfo()
  for k, v in fi.fldtype.items():
    print(f"FLDTYPE '{k}':")
    print('  standout:', v.standout);  comb.standout.update(v.standout)
    print('  inpmode:', v.inpmode); comb.inpmode.update(v.inpmode)
    print('  signed:', v.signed); comb.signed.update(v.signed)
    print('  zeros:', v.zeros); comb.zeros.update(v.zeros)
    print('  typlzero:', v.typlzero); comb.typlzero.update(v.typlzero)
    print('  convert:', v.convert); comb.convert.update(v.convert)
    print('  showhelp:', v.showhelp); comb.showhelp.update(v.showhelp)
    print('  wholenum:', v.wholenum); comb.wholenum.update(v.wholenum)
    print('  deftyp:', v.deftyp); comb.deftyp.update(v.deftyp)
  print('COMBINED:')
  print('  standout:', comb.standout)
  print('  inpmode:', comb.inpmode)
  print('  signed:', comb.signed)
  print('  zeros:', comb.zeros)
  print('  typlzero:', comb.typlzero)
  print('  convert:', comb.convert)
  print('  showhelp:', comb.showhelp)
  print('  wholenum:', comb.wholenum)
  print('  deftyp:', comb.deftyp)
  
if __name__ == '__main__':
  main()
