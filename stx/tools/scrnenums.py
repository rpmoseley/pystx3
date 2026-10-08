'''
This module provides the various enumerations of the flags that are present in the screen entity files.
This enables applications to determine the appropriate values directly from the database.
'''

import enum
__all__ = ('EntityType',
           'EntityFormatClear',
           'EntityFormatRepeat',
           'EntityFieldAction', 
           'EntityFieldCase',
           'EntityFieldDefault',
           'EntityFieldFlag', 
           'EntityFieldMode',
           'EntityFieldOption', 
           'EntityFieldStatus',
           'EntityFieldType', 
           'EntityFieldZeros', 
           'EntityValtabType',
           
           'LegacyFormatRepeat',
           'LegacyFieldCase',
           'LegacyFieldDefault',
           'LegacyFieldFlag', 
           'LegacyFieldMode',
           'LegacyFieldOption', 
           'LegacyFieldStatus',
           'LegacyFieldType',
           'LegacyFieldZeros',
           'LegacyValtabType',
           
           'all_enums')

class LegacyMap:
  def __init__(self, values=None, func=None):
    if func:
      if not isinstance(values, str):
        raise TypeError('If passing callback function, provide valid values as a str')
    else:
      if not isinstance(values, dict):
        raise TypeError('Pass dictionary of valid values to new enum')
    self._map = values 
    self.filter = func

  def __call__(self, key, *args):
    if self.filter is None:
      return self._map.get(key, None)
    elif key not in self._map:
      return None
    else:
      return self.filter(key, *args)

# Type of entity on screen entity database
class EntityType(enum.IntEnum):
  FORMAT = 1
  WINDOW = 2
  POPMENU = 3
  BARMENU = 4
  VALTAB = 5
  MASK = 6

# Screen format CLEAR flag values
class EntityFormatClear(enum.IntEnum):
  NOCLEAR = 0
  STANDCLEAR = 1
  WIDECLEAR = 2
    
# Screen format status values
class EntityFieldStatus(enum.IntEnum):
  NOTHING = 0
  PROMPT = 1
  DISPLAY = 2
  BOTH = 3
  REPROMPT = 4
LegacyFieldStatus = LegacyMap({
  'B': EntityFieldStatus.BOTH,
  'D': EntityFieldStatus.DISPLAY,
  'N': EntityFieldStatus.NOTHING,
  'P': EntityFieldStatus.PROMPT,
  'R': EntityFieldStatus.REPROMPT,
})
    
# Screen format field type
class EntityFieldType(enum.IntEnum):
  ALPHA = 0
  ALPHANUM = 1
  TEXT = 2
  NUMERIC = 3
  DATE = 4
  TIME = 5
  MONEY = 6
  CURRENCY = 7
LegacyFieldType = LegacyMap({
  'A': EntityFieldType.ALPHA,
  'C': EntityFieldType.ALPHANUM,
  'D': EntityFieldType.DATE,
  'F': EntityFieldType.CURRENCY,
  'H': EntityFieldType.TIME,
  'M': EntityFieldType.MONEY,
  'N': EntityFieldType.NUMERIC,
  'T': EntityFieldType.TEXT, 
})

# Screen format repeat types
class EntityFormatRepeat(enum.IntEnum):
  HORIZONTAL = 0
  LINE_WRAP = 1
  VERTICAL = 2
  SCROLL = 3
  COLUMN = 4
  NEXTFORM = 5
LegacyFormatRepeat = LegacyMap({
  'C': EntityFormatRepeat.COLUMN,
  'H': EntityFormatRepeat.HORIZONTAL,
  'L': EntityFormatRepeat.LINE_WRAP,
  'N': EntityFormatRepeat.NEXTFORM,
  'S': EntityFormatRepeat.SCROLL,
  'V': EntityFormatRepeat.VERTICAL,
})

# Screen format input modes
class EntityFieldMode(enum.IntFlag):
  NONE = 0x00
  INPUT = 0x01
  OUTPUT = 0x02
  SPECIAL = 0x04
  AUTOACCEPT = 0x10
LegacyFieldMode = LegacyMap({
  'i': EntityFieldMode.INPUT | EntityFieldMode.AUTOACCEPT, 
  'I': EntityFieldMode.INPUT,
  'o': EntityFieldMode.OUTPUT | EntityFieldMode.AUTOACCEPT, 
  'O': EntityFieldMode.OUTPUT,
  'N': EntityFieldMode.NONE, 
  's': EntityFieldMode.SPECIAL | EntityFieldMode.AUTOACCEPT, 
  'S': EntityFieldMode.SPECIAL,
})

# Screen format signed and date field types, this corresponds to the legacy
# 'signed' field for the fields within a format.
class EntityFieldOption(enum.IntEnum):
  NONE_BLANKS = 0              # No blanks, application can set blanks
  NOAPP_BLANKS = 1             # No blanks, application cannot set blanks
  BLANKS = 2                   # Allow blanks
  SIGNED = 3                   # Signed field
  UNSIGNED = 4                 # Unsigned field
  PARTIAL = 5                  # Allow partial field value
  SEARCHABLE = 6               # Permit searchs on field
  DEFAULT = 7                  # Default field value
  FULL = 8                     # Require full field value
def _conv_option(option, fldtype):
  # Convert the legacy 'signed' field to the corresponding value according to the field type
  #             A     B      C          F    N    P       S      U        Y
  # ALPHA    => NOAPP BLANKS                 NONE                UNSIGNED 
  # ALPHANUM => NOAPP BLANKS                 NONE         SIGNED UNSIGNED
  # TEXT     => NOAPP BLANKS                 NONE         SIGNED UNSIGNED
  # NUMERIC  =>       BLANKS SEARCHABLE      NONE         SIGNED UNSIGNED PARTIAL
  # DATE     =>                         FULL NONE PARTIAL                 DEFAULT
  # TIME     =>       BLANKS            FULL NONE PARTIAL SIGNED UNSIGNED DEFAULT
  # MONEY    =>       BLANKS                              SIGNED UNSIGNED PARTIAL
  # CURRENCY =>       BLANKS                 NONE         SIGNED UNSIGNED PARTIAL
  match option:
    case 'A':
      if fldtype in (EntityFieldType.ALPHA, EntityFieldType.ALPHANUM, EntityFieldType.TEXT):
        return EntityFieldOption.NOAPP_BLANKS
    case 'B':
      if fldtype != EntityFieldType.DATE:
        return EntityFieldOption.BLANKS
    case 'C':
      if fldtype == EntityFieldType.NUMERIC:
        return EntityFieldOption.SEARCHABLE
    case 'F':
      if fldtype in (EntityFieldType.DATE, EntityFieldType.TIME):
        return EntityFieldOption.FULL
    case 'N':
      if fldtype != EntityFieldType.MONEY:
        return EntityFieldOption.NONE_BLANKS
    case 'P':
      if fldtype in (EntityFieldType.TEXT, EntityFieldType.NUMERIC, EntityFieldType.DATE, EntityFieldType.TIME):
        return EntityFieldOption.PARTIAL
    case 'S':
      if fldtype not in (EntityFieldType.ALPHA, EntityFieldType.DATE):
        return EntityFieldOption.SIGNED
    case 'U':
      if fldtype != EntityFieldType.DATE:
        return EntityFieldOption.UNSIGNED
    case 'Y':
      if fldtype in (EntityFieldType.DATE, EntityFieldType.TIME):
        return EntityFieldOption.DEFAULT
      elif fldtype in (EntityFieldType.NUMERIC, EntityFieldType.MONEY, EntityFieldType.CURRENCY):
        return EntityFieldOption.PARTIAL
  raise ValueError(f'Option: {option} with {fldtype.name}')
LegacyFieldOption = LegacyMap('ABCFNPSUY', _conv_option)

# Screen format case conversions
class EntityFieldCase(enum.IntEnum):
  LOWER = 0
  UPPER = 1
  CAPITALISE = 2
LegacyFieldCase = LegacyMap({
  'C': EntityFieldCase.CAPITALISE,
  'L': EntityFieldCase.LOWER,
  'U': EntityFieldCase.UPPER,
})

# Screen format field action types
class EntityFieldAction(enum.IntFlag):
  NOTHING = 0x00
  PROMPT = 0x01
  DISPLAY = 0x02
  CHANGED = 0x04
  REPROMPT = 0x08
  NOTSET = 0x10
  NOPROMPT = 0x20

'''
Macros used in legacy code
ISPROMPT(a)      (a & EntityFieldAction.PROMPT)
ISDISPLAY(a)     (a & EntityFieldAction.DISPLAY)
ISCHANGED(a)     (a & EntityFieldAction.CHANGED)
ISNOTHING(a)     (a == EntityFieldAction.NOTHING)
ISREPROMPT(a)    (a & EntityFieldAction.REPROMPT)
ISNOPROMPT(a)    (a & EntityFieldAction.NOPROMPT)
UNSETPROMPT(a)   (a &= ~EntityFieldAction.PROMPT)
UNSETDISPLAY(a)  (a &= ~EntityFieldAction.DISPLAY)
UNSETSCHANGED(a) (a &= ~EntityFieldAction.CHANGED)
UNSETREPROMPT(a) (a &= ~EntityFieldAction.REPROMPT)
UNSETNOPROMPT(a) (a &= ~EntityFieldAction.NOPROMPT)
SETPROMPT(a)     (a |= EntityFieldAction.PROMPT; a &= EntityFieldAction.NOPROMPT)
SETDISPLAY(a)    (a |= EntityFieldAction.DISPLAY)
SETCHANGED(a)    (a |= EntityFieldAction.CHANGED)
SETREPROMPT(a)   (a |= EntityFieldAction.REPROMPT)
SETNOTHING(a)    (a = EntityFieldAction.NOTHING)
SETNOPROMPT(a)   (a |= EntityFieldAction.NOPROMPT)
'''

# Screen format field zeros types
class EntityFieldZeros(enum.IntFlag):
  BLANK = 0
  SUPPRESS = 1
  FULL = 2
LegacyFieldZeros = LegacyMap({
  'B': EntityFieldZeros.BLANK,
  'F': EntityFieldZeros.FULL,
  'S': EntityFieldZeros.SUPPRESS,
})

# Screen format default group types
class EntityFieldDefault(enum.IntEnum):
  TAKEDEFONLY = 0
  TAKEANDSET = 1
  SETDEFKEY = 2
  SETDEFAPP = 3
  SETDEFBOTH = 4
LegacyFieldDefault = LegacyMap({
  'a': EntityFieldDefault.TAKEDEFONLY,
  'b': EntityFieldDefault.SETDEFBOTH,
  'c': EntityFieldDefault.TAKEANDSET,
  'd': EntityFieldDefault.SETDEFKEY,
  'e': EntityFieldDefault.SETDEFAPP,
})  
  
# Screen format field flag
class EntityFieldFlag(enum.IntFlag):
  SHOWHELP = 0x01
  WHOLENUM = 0x02
def LegacyFieldFlag(showhelp, wholenum):
  retval = 0x00 if showhelp in ' N' else EntityFieldFlag.SHOWHELP
  retval |= 0x00 if wholenum in ' N' else EntityFieldFlag.WHOLENUM
  return retval
  
# Screen validation table types
class EntityValtabType(enum.IntEnum):
  NONE = 0
  RANGE = 1
  MATCH = 2
  SUBSTITUTE = 3
  TABLE = 4
  MASKVALID = 5
LegacyValtabType = LegacyMap({
  'K': EntityValtabType.MASKVALID,
  'M': EntityValtabType.MATCH,
  'N': EntityValtabType.NONE,
  'R': EntityValtabType.RANGE,
  'S': EntityValtabType.SUBSTITUTE,
  'T': EntityValtabType.TABLE,
})

all_enums = [
  (EntityFieldAction, 'fldaction', EntityType.FORMAT),
  (EntityFieldCase, 'fldcase', EntityType.FORMAT),
  (EntityFieldDefault, 'flddefault', EntityType.FORMAT),
  (EntityFieldMode, 'fldmode', EntityType.FORMAT),
  (EntityFieldOption, 'fldopt', EntityType.FORMAT),
  (EntityFieldStatus, 'fldstat', EntityType.FORMAT),
  (EntityFieldType, 'fldtype', EntityType.FORMAT),
  (EntityFieldZeros, 'fldzero', EntityType.FORMAT),
  (EntityFormatClear, 'frmclear', EntityType.FORMAT),
  (EntityFormatRepeat, 'frmrepeat', EntityType.FORMAT),
  (EntityValtabType, 'valtype', EntityType.VALTAB), 
]
