'''
This variant provides a version that provides a command hanlder that also outputs debug messages.
It makes use of the current UI module to maintain the correct state of the driver.
'''

from .common import CommandCore

class Command(CommandCore):
  # Command: 0x2d
  def GPUpdate(self, farg):
    gname, gvalue = farg
    print(f'GPUPDATE: {gname} -> {gvalue}', file=self.dfd)
      
  # Command: 0x30
  def PopOpen(self, farg):
    if self._resume:
      self._resume = None
    else:
      pname, poption = farg
    if self._fxon:
      print(f"POPOPEN: {pname}.{poption} -> FASTEXIT", file=self.dfd)
    else:
      # FIXME: Handle the particular popmenu.poption approprately
      # FIXME: For now always send the same selected option
      print(f"POPOPEN: {pname}.{poption} -> 'A'", file=self.dfd)
      self.send('s', 'A')

  # Command: 0x32
  def PopOnOff(self, farg):
    pname, poption, ponoff = farg
    print(f'POPONOFF: {pname}.{poption} -> {ponoff}', file=self.dfd)

  # Command: 0x41
  def OpenWindow(self, farg):
    wname = farg[0]
    print(f'OPENWIND: {wname}', file=self.dfd)

  # Command: 0x4c
  def LoadFormat(self, farg):
    fname, fchksum = farg
    self.send('c', '1')
    print(f'LOADFORMAT: {fname}, {fchksum} -> 1', file=self.dfd)

  # Command: 0x52
  def ReadFormat(self):
    for fnum in range(13):
      fact, fdisp, fhlp = self.receive('bcV')
      print(f"READFORMAT: FLD: {fnum}: ({fact}, '{fdisp}', {fhlp})", file=self.dfd)
    frec = self.receive('r')[0]
    print(f'READFORMAT: REC: {frec}', file=self.dfd)
    self.send('B', True)

  # Command: 0x59
  def ChangeType(self, farg):
    fnum, fmod = farg
    print(f"CHTYPE: {fnum} -> '{fmod}'", file=self.dfd)
    
  # Command: 0x5a
  def TraceLevel(self):
    print('TRACELEVEL: (0, 0, 0, 0, 0)', file=self.dfd)
    self.send('hhhhh', 0, 0, 0, 0, 0)

  # Command: 0x61
  def CloseWindow(self, farg):
    wname = farg[0]
    print(f'CLOSEWIND: {wname}', file=self.dfd)

  # Command: 0x64
  def WipeFormat(self, farg):
    fname = farg[0]
    print(f'WIPEFORMAT: {fname}', file=self.dfd)

  # Command: 0x67
  def NameWindow(self):
    print('NAMEWINDOW: None', file=self.dfd)
    self.send('s', '')

