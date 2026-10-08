'''
This support module provides shared functionality for handling text files which contain
information usually used at runtime by the screen driver.
'''

__all__ = ('unpack', 'unpack_dict')

#
# The following exception and function provide a means for splitting up data into
# fields consists of the format given.
#

class UnpackError(ValueError):
  pass

def unpack(fmt, fd_or_data, single=False):
  '''Take a format of the form: %[n]t, and return a tuple of suitably converted values.
     n if omitted, defaults to a single byte
     t is one of the following:
        b  - raw byte value
        c  - character representation of byte(s)
        d  - integer value of byte(s)
        f  - byte(s) converted to boolean if set to 'Y' or '1'
        h  - hexidecimal value of byte(s)
        l  - rest of line converted to str(), right stripped
        L  - rest of line converted to str()
        s  - byte(s) converted to str(), right stripped
        S  - byte(s) converted to str()
        *  - byte(s) are skipped and ignored
        Any other characters are skipped and not converted.
  '''
  fmtoff = 0       # Offset within format
  datoff = 0       # Offset within data
  retval = list()  # List of values found within data bytes
  data = fd_or_data if isinstance(fd_or_data, (bytes, str)) else fd_or_data.readline()
  isstr = isinstance(data, str)
  while fmtoff < len(fmt) and datoff < len(data):
    match fmt[fmtoff]:
      case '%':
        # Possible conversion sequence
        fmtoff += 1
        begdig = fmtoff
        while fmt[fmtoff].isdigit():
          fmtoff += 1
        sizseq = 1 if begdig == fmtoff else int(fmt[begdig:fmtoff])
        match fmt[fmtoff]:
          case '*':
            # Ignore the number of bytes 
            pass
          case '%':
            # Ignore the percent character
            if sizseq > 1 or fmt[fmtoff-1] != '%':
              raise UnpackError('Percent can only appear after another percent ("%%")')
          case 'b':
            # Append the number of individual bytes
            retval.extend(data[datoff+n] for n in range(sizseq))
          case 'c':
            # Append the number of individual bytes as characters
            if isstr:
              retval.extend(data[datoff+n] for n in range(sizseq))
            else:
              retval.extend(chr(data[datoff+n]) for n in range(sizseq))
          case 'd':
            # Convert the bytes to a decimal number
            retval.append(int(data[datoff:datoff + sizseq]))
          case 'f':
            # Convert the bytes to booleans
            if isstr:
              retval.extend(data[datoff + n] in 'YT1' for n in range(sizseq))
            else:
              retval.extend(data[datoff + n] in b'YT1' for n in range(sizseq))
          case 'h':
            # Convert the bytes representing a hexidecimal number
            retval.append(int(data[datoff:datoff + sizseq], 16))
          case 'l'|'L':
            # Decode the rest of line as a single string
            strval = data[datoff:-1] if isstr else data[datoff:-1].decode('iso8859-1')
            datoff += len(strval)
            retval.append(strval if fmt[fmtoff].isupper() else strval.rstrip())
          case 's'|'S':
            # Decode the bytes into a string
            strval = data[datoff:datoff+sizseq] if isstr else data[datoff:datoff+sizseq].decode('iso8859-1')
            retval.append(strval if fmt[fmtoff].isupper() else strval.rstrip())
          case _:
            # Complain about the unpacking
            raise ValueError(f'Unable to unpack data: {fmt[fmtoff]}')
        datoff += sizseq
      case _:
        if isstr:
          if fmt[fmtoff] != data[datoff]:
            raise UnpackError(f"Unexpected literal '{data[datoff]}' expecting '{fmt[fmtoff]}'")
        elif fmt[fmtoff] != chr(data[datoff]):
          raise UnpackError(f"Unexpected literal '{chr(data[datoff])}' expecting '{fmt[fmtoff]}'")
        datoff += 1
    fmtoff += 1
  if fmtoff < len(fmt):
    raise UnpackError(f'Format has not been completely used: {fmtoff}')
  return retval[0] if single else retval

class UnpackDict:
  'Variant of dict() adding attribute access for values'
  def __init__(self):
    super().__setattr__('_info', dict())
  
  def keys(self):
    return self._info.keys()
  
  def __getitem__(self, name):
    return self._info.__getitem__(name)
  
  def __setitem__(self, name, value):
    self._info.__setitem__(name, value)
    
  def __getattr__(self, name):
    return self._info.__getitem__(name)
  
  def __setattr__(self, name, value):
    self._info.__setitem__(name, value)
      
  def __repr__(self):
    return repr(self._info)
  
  
def unpack_dict(fmt, fd_or_data):
  '''Take a format of the form: {[n]t:f[;f]} and return a dictionary of suitably converted values.
     n if ommitted defaults to a single byte
     t is one of the following:
        b  - raw byte value
        c  - character represnetation of byte(s)
        d  - integer value of byte(s)
        f  - byte(s) converted to boolean if set to 'Y' or '1'
        h  - hexidecimal value of byte(s)
        l  - rest of line converted to str(), right stripped
        L  - rest of line converted to str()
        s  - byte(s) converted to str(), right stripped
        S  - byte(s) converted to str()
        *  - byte(s) are skipped and ignored
      Any other characters are skipped and ignored, to skip '{' or '}' double the character.
  '''
  def chkliteral(chk):
    if isstr:
      if data[datoff] != chk:
        raise UnpackError(f"Expected '{chk}', got '{data[datoff]}'")
    elif chr(data[datoff]) != chk:
      raise UnpackError(f"Expected '{chk}', got '{chr(data[datoff])}'")

  def convbool(val):
      return (val in 'YT1') if isstr else (val in b'YT1')
  
  fmtoff = 0         # Offset within format
  datoff = 0         # Offset within data
  retval = UnpackDict()
  data = fd_or_data if isinstance(fd_or_data, (bytes, str)) else fd_or_data.readline()
  isstr = isinstance(data, str)
  while fmtoff < len(fmt) and datoff < len(data):
    match fmt[fmtoff]:
      case '{':
        fmtoff += 1
        # Possible conversion
        if fmt[fmtoff] == '{':
          # Skip past an explicit '{' in data
          chkliteral('{')
          datoff += 1
          fmtoff += 1
        elif fmt[fmtoff] == '%':
          raise UnpackError(f"Cannot mix '%' and '{...}' sequences at {fmt[fmtoff:]}")
        elif fmt[fmtoff] == '}':
          raise UnpackError(f'Cannot handle empty conversioni at {fmt[fmtoff:]}')
        elif fmt[fmtoff] == '?':
          # Use rest of line for conversion
          convsize = 0
        elif fmt[fmtoff].isdigit():
          # Handle the repeat count
          cur = fmtoff
          while fmt[fmtoff].isdigit():
            fmtoff += 1
          convsize = int(fmt[cur:fmtoff])
        else:
          # Assume repeat count of a single byte
          convsize = 1
          
        if fmt[fmtoff] == '*':
          # Handle ignored conversion immediately
          if fmt[fmtoff+1] == ':':
            # Skip optional name
            while fmt[fmtoff+1] != '}':
              fmtoff += 1
          # Check termination brace present
          if fmt[fmtoff+1] != '}':
            raise UnpackError(f'Cannot name an ignored conversion at {fmt[fmtoff:]}')
          fmtoff += 2
          datoff += convsize
          continue
        elif fmt[fmtoff] not in 'bcdfhlLsS':
          raise UnpackError('Unhandled type of conversion at {fmt[fmtoff:]}')
        elif fmt[fmtoff] in 'lL' and convsize > 1:
          raise UnpackError(f'Cannot have multiple line conversions at {fmt[fmtoff:]}')
        elif fmt[fmtoff+1] == '}':
          raise UnpackError(f'Cannot have unnamed conversion at {fmt[fmtoff:]}')
        elif fmt[fmtoff+1] != ':':
          raise UnpackError(f'Missing separator in conversion at {fmt[fmtoff:]}')
        else:
          convtype = fmt[fmtoff]
          fmtoff += 2
          cur = fmtoff
          while fmtoff < len(fmt):
            while fmt[fmtoff].isalnum():
              fmtoff += 1
            if fmt[fmtoff] != ';':
              break
            fmtoff += 1
          if fmt[fmtoff] != '}':
            raise UnpackError(f'Unterminated conversioni at {fmt[fmtoff:]}')
          convname = str(fmt[cur:fmtoff]).split(';')
          if convtype in 'cf' and len(convname) != convsize:
            raise UnpackError(f'Expected {convsize} names, got {len(convname)}, at {fmtoff}')
            
        # Handle the conversion appropriately
        if convtype in 'bcf':
          for n in range(convsize):
            match convtype:
              case 'b':
                retval[convname[n]] = data[datoff+n]
              case 'c':
                retval[convname[n]] = data[datoff+n] if isstr else chr(data[datoff+n])
              case 'f':
                retval[convname[n]] = convbool(data[datoff+n])
          datoff += convsize
        elif convtype in 'dh':
          try:
            match convtype:
              case 'd':
                retval[convname[0]] = int(data[datoff:datoff+convsize])
              case 'h':
                retval[convname[0]] = int(data[datoff:datoff+convsize], 16)
          except ValueError:
            raise UnpackError(f'Bad numeric conversion at {fmt[fmtoff:]}')
          datoff += convsize
        else:
          match convtype:
            case 'l' | 'L':
              strval = data[datoff:-1] if isstr else data[datoff:-1].decode('iso8859-1')
              datoff += len(strval)
            case 's' | 'S':
              strval = data[datoff:datoff+convsize] if isstr else data[datoff:datoff+convsize].decode('iso8859-1')
              datoff += convsize
          retval[convname[0]] = strval if convtype.isupper() else strval.rstrip()
      case _:
        chkliteral(fmt[fmtoff])
        datoff += 1
    fmtoff += 1
  if fmtoff < len(fmt):
    raise UnpackError(f'Format has not been completely used, {fmtoff} ({fmt[fmtoff]}) and {fmt}')
  return retval

if __name__ == '__main__':
  data='Change Users Password                            C0C#000003e1N  '
  htxt='Select this option to change the password of a selected user.'
  fmt = '{40s:text}{9s:submenu}{c:option}{*}{c:retcode}#{7*}{d:numhelp}{3c:disabled;secgrp;seclev}'
  print(unpack_dict(fmt, data))
