'''
This module provids the processing of mode for each member within an archive, and sub-archives, within
that archive.
'''

import fnmatch
try:
  from .enums import ReqMode
except ImportError:
  from enums import ReqMode

# Mapping item class
class ModeMapItem:
  def __init__(self, mode, dirs=None):
    if not isinstance(mode, ReqMode):
      raise TypeError('Member must be a valid ReqMode value')
    if dirs and not isinstance(dirs, ReqMode):
      raise TypeError('Archives must be a valid ReqMode value')
    self.mode = mode                        # Default mode of non-archive members
    self.dirs = dirs                        # Default mode of directories
    self.arch = None                        # Embedded archive or directory members
    
  def __repr__(self):
    return f'ModeMapItem({self.mode!r}, {self.dirs!r}, {self.arch!r})'
  
  def __eq__(self, other):
    if not isinstance(other, ModeMapItem):
      return False
    if self.mode != other.mode:
      return False
    if self.dirs != other.dirs:
      return False
    if self.arch and other.arch:
      return self.arch == other.arch
    return not self.arch and not other.arch
  
  def get(self, name):
    '''Implement member fetch from the associated dictionary, if present'''
    return None if self.arch is None else self.arch.get(name, None)

  def get_mode(self, name):
    '''Return the mode for the given member using the associated dictionary, if present'''
    if self.arch is None:
      # No associated dictionary, return our mode
      return self.mode
    
    ent = self.arch.get(name, None)
    if ent is None:
      # No entry, return our mode
      return self.mode
    elif isinstance(ent, ModeMapItem):
      # Return the mode stored on the mapping
      return ent.mode
    elif isinstance(ent, ReqMode):
      # Return the mode stored directly
      return ent
    else:
      raise ValueError('Corrupt mapping')
        
  def set(self, name, mode, dirs=None):
    '''Add a member to the associated dictionary, creating it first, if
      required, set the member and archive modes if the member is an archive.'''
    if name.find('/') >= 0:
      raise ValueError('Name cannot contain paths')
    if not isinstance(mode, ReqMode):
      raise ValueError('Member must be a ReqMode value')
    if dirs is not None and not isinstance(dirs, ReqMode):
      raise ValueError('Directory must be a ReqMode value')
    if self.arch is None:
      # Create a new dictionary with the contents of the new member
      self.arch = dict()
      ent = self.arch[name] = mode if dirs is None else ModeMapItem(mode, dirs)
    else:         
      # Check if an existing entry in dictionary
      ent = self.arch.get(name, None)
      if ent is None:
        # Add a new entry for a member
        ent = self.arch[name] = mode if dirs is None else ModeMapItem(mode, dirs)
      elif isinstance(ent, ModeMapItem):
        # Update the mode of the mapping
        ent.mode = mode
        if dirs is not None:
          ent.dirs = dirs
      elif isinstance(ent, ReqMode):
        # Update the mode of the mapping
        ent = self.arch[name] = mode
      else:
        # Corrupt mapping
        raise ValueError('Entry has the wrong type')
    return ent
      
  def get_make(self, name, mode, dirs=None):
    '''Return the archive member or create it if missing, if the member exists as
    a non-archive, raise error.'''
    ent = None if self.arch is None else self.get(name)
    if ent is None:
      # Create a new entry, including the associated dictionary
      ent = self.set(name, mode, dirs)
    elif not isinstance(ent, ModeMapItem):
      raise ValueError('Cannot add to non-archive member')
    return ent
              
class Required:
  def __init__(self, mode=ReqMode.SKIP, dirs=ReqMode.SKIP):
    self._map = ModeMapItem(mode, dirs)
  
  def __repr__(self):
    return repr(self._map)

  def add(self, mempath: str|None, memname: str|list[str]|tuple[str]|None, mode: ReqMode=ReqMode.FILEOBJ, dirs: ReqMode|None = None) -> None:
    '''Add MEMNAME to the mapping for MEMPATH with MODE.
    If no MEMPATH then the main mapping is amended.
    If no MEMNAME is given then the default mode is amended.'''
    if mode is not None and not isinstance(mode, ReqMode):
      raise ValueError('Pass a mode that is specified in the ReqMode enum')
    if mempath is not None and not isinstance(mempath, str):
      raise ValueError('Either pass None or a str for the member path')
    if isinstance(memname, str):
      if memname.find('/') > 0:
        raise ValueError('Cannot pass members containing pathnames')
    elif isinstance(memname, dict):
      for k, v in memname.items():
        if not isinstance(k, str):
          raise ValueError('Dictionary must have str keys')
        if isinstance(v, tuple):
          match len(v):
            case 1:       # (MODE,)
              if not isinstance(v[0], ReqMode):
                raise ValueError('Mode must be a ReqMode')
            case 2:       # (MODE, DIRS)
              if not isinstance(v[0], ReqMode):
                raise ValueError('Mode must be a ReqMode')
              if v[1] is not None and not isinstance(v[1], ReqMode):
                raise ValueError('Dirs must be a ReqMode')
            case _:       # Invalid
              raise ValueError('Invalid mode given')
        elif not isinstance(v, ReqMode):
          raise ValueError('Mode must be a (m,), (m,d) or m, all ReqMode')
    elif isinstance(memname, (tuple, list)):
      if not all([isinstance(m, str) for m in memname]):
        raise ValueError('Must provide str members')
      elif not all([m.find('/') < 0 for m in memname]):
        raise ValueError('Must not provide pathname for members')
    elif memname is not None:
        raise ValueError('Invalid addition attempted')

    updmap = self._map
    if mempath is not None:
      # Locate the appropriate mapping for the archive path
      beg, end = 0, mempath.find('/')
      while end > 0:
        part = mempath[beg:end]
        beg = end + 1
        end = mempath.find('/', beg)
        updmap = updmap.get_make(part, ReqMode.SKIP, ReqMode.SKIP)
      else:
        part = mempath[beg:]
        updmap = updmap.get_make(part, ReqMode.SKIP, ReqMode.SKIP)
        
    if memname is None:
      # Update the default mode for the current mapping
      updmap.mode = mode
      if dirs is not None:
        updmap.dirs = dirs
    elif isinstance(memname, (tuple, list)):
      # Add entries for all the members
      for name in memname:
        updmap.set(name, mode, dirs)
    elif isinstance(memname, dict):
      # Add entrires for each member in the given dictionary
      for k, v in memname.items():
        if isinstance(v, tuple):
          match len(v):
            case 1:           # Member mode only
              updmap.set(k, v[0])
            case 2:           # Member and directory mode
              updmap.set(k, v[0], v[1])
        elif isinstance(v, ReqMode):
          updmap.set(k, v)
    elif isinstance(memname, str):
      # Add a new entry for the given member
      updmap.set(memname, mode, dirs)

class RequiredCursor:
  def __init__(self, reqd: Required) -> None:
    self._reqd = reqd
    self._curmap = reqd._map

  @property
  def current_map(self) -> ModeMapItem:
    'Return the current mapping being used'
    return self._curmap or self._reqd._map

  def change_map(self, path: str | None, actmap: ModeMapItem | None = None) -> ModeMapItem:
    'Change the current mapping given the PATH and the optional ACTMAP which defaults to root'
    curmap = actmap or self._reqd._map
    if path is None or path == '':
      return curmap
    beg, end = 0, path.find('/')
    while end > 0:
      part = path[beg:end]
      beg = end + 1
      end = path.find('/', beg)
      nxtmap = curmap.get(part)
      if not isinstance(nxtmap, ModeMapItem):
        return None
      curmap = nxtmap
    else:
      part = path[beg:]
      nxtmap = curmap.get(part)
      if not isinstance(nxtmap, ModeMapItem):
        return None
      curmap = nxtmap
    return curmap

  @property
  def root_map(self) -> ModeMapItem:
    'Return the root mapping'
    return self._reqd._map

  def get(self, path: str, actmap: ModeMapItem | None = None) -> ReqMode | tuple[ReqMode, ReqMode]:
    'Return the mode information for the given PATH using the ACTMAP or the root mapping'
