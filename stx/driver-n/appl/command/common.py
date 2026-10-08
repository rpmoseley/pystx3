'''
This module provides the common functionality and state shared by all other variants
'''

# Import the comms subpackage so that it can be used
from ..comms import Comm

# Define the mapping from command byte to the actual function and optionally expected types of values
# from the application.
_cmdmap = {
  0x21: 'Background',
  0x22: 'PrModify',
  0x23: 'SetCurrency',
  0x24: 'ShowHelp',
  0x25: 'ScrUpd',
  0x26: 'MentorWord',
  0x28: 'GetGName',
  0x29: 'PrDup',
  0x2a: 'FindVT',
  0x2b: 'SystemRequest',
  0x2c: 'GPGet',
  0x2d: ('GPUpdate', 'ss'),
  0x2e: 'FastExit',
  0x2f: 'Dialogue',
  0x30: ('PopOpen', 'ss'),
  0x31: 'PopClose',
  0x32: ('PopOnOff', 'ssB'),
  0x33: 'PopAt',
  0x34: 'PopText',
  0x35: 'PopCreate',
  0x36: 'PopAppend',
  0x37: 'PopDelete',
  0x38: 'PopData',
  0x39: 'FormAlias',
  0x3c: 'CanRun',
  0x3d: 'GraphCtrl',
  0x3e: 'MWordCallback',
  0x40: 'AppReadChar',
  0x41: ('OpenWindow', 's'),
  0x42: 'RunProgram',
  0x43: 'ClearFormat',
  0x44: 'DetachMe',
  0x45: 'ChangeLength',
  0x46: 'ChangeMessage',
  0x47: 'InterruptOn',
  0x48: 'InterruptOff',
  0x49: 'MessageOn',
  0x4a: 'MessageOff',
  0x4b: 'KillMe',
  0x4c: ('LoadFormat', 'si'),
  0x4d: 'MessageScreen',
  0x4e: 'SuspendMe',
  0x4f: 'StartPrint',
  0x50: 'NewPrint',
  0x51: 'FormData',
  0x52: 'ReadFormat',
  0x53: 'SuspendMe',
  0x54: 'TitleScreen',
  0x55: 'EndPrint',
  0x56: 'DebugMenu',
  0x57: 'WriteFormat',
  0x58: 'ChangePosition',
  0x59: ('ChangeType', 'hc'),
  0x5a: 'TraceLevel',
  0x5b: 'ChPosTemp',
  0x5c: 'PrNewJob',
  0x5d: 'ConfMessage',
  0x5e: 'WriteMessage',
  0x61: ('CloseWindow', 's'),
  0x62: 'Blank',
  0x63: 'ClearScreen',
  0x64: ('WipeFormat', 's'),
  0x65: 'DeDump',
  0x66: 'LoseChar',
  0x67: 'NameWindow',
  0x68: 'TypeAhead',
  0x69: 'SizeWind',
  0x6a: 'FormNLoad',
  0x6b: 'IsWindDisplay',
  0x6c: 'LogComment',
  0x6d: 'WindDefine',
  0x6e: 'NumberDecimals',
  0x6f: 'WindData',
  0x70: 'PrintScreen',
  0x71: 'Repeats',
  0x72: 'FldCurr',
  0x73: 'SetDecimals',
  0x74: 'ToolInfo',
  0x75: 'LastChar',
  0x76: 'ScroolDir',
  0x77: 'WidthScreen',
  0x78: 'KeyWait',
  0x79: 'FormFLoad',
  0x7a: 'GetVirtual',
  0x7b: 'IsSuspended',
  0x7c: 'AppHotKey',
  0x7d: 'PTitleScreen',
  0x7e: 'Search',
  0x7f: 'Browse',
}

class CommandCore(Comm):
  def process(self, cmd, *args, **kwds):
    # Handle according to type of command given
    if isinstance(cmd, (bytes, bytearray)):
      byt = cmd[0]
    elif isinstance(cmd, str):
      byt = ord(cmd[0])
    elif isinstance(cmd, int):
      byt = cmd
    else:
      raise NotImplementedError(cmd)
    
    # Call the appropriate handler, preprocessing any expected input first
    finfo = _cmdmap.get(byt, None)
    if isinstance(finfo, tuple):
      # Handle any preprocessing expected
      fargs = self.receive(finfo[1])
      if func := getattr(self, finfo[0], None):
        return func(fargs, *args, **kwds)
      elif func := getattr(self, 'Default', None):
        return func(finfo[0], fargs, *args, **kwds)
    elif finfo is None:
      raise ValueError(f'**UNKNOWN**: {byt}')
    elif func := getattr(self, finfo, None):
      return func(*args, **kwds)
    elif func := getattr(self, 'Default', None):
      return func(byt, *args, **kwds)
