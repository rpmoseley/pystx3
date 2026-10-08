'''
Create the formats database for use with the driver package, this will create a SQLite3 database and populate it
with the contents of the uk.txz member of the given archive. This will store all the information available only
from the text files that are created and not stored in the utool database.

Only the UK language formats will be processed, no user tailored or transient tables are handled either.
'''

import itertools
import re
import os.path
try:
  from .message import Message
  from .namespace import Namespace
  from .sqlsupp import SqlSupport, SqlSupportError
  from .textutil import UnpackError, unpack, unpack_dict
  from .tarutil import Archive, ReqMode
  from .scrnenums import * 
except ImportError:
  from message import Message
  from namespace import Namespace
  from sqlsupp import SqlSupport, SqlSupportError
  from textutil import UnpackError, unpack, unpack_dict
  from tarutil import Archive, ReqMode
  from scrnenums import * 

# Specialisation providing information particular to formats
class FormatArchive(Archive):
  def __init__(self, tarname, lang='uk'):
    super().__init__(tarname)
    self._lang = lang

  def is_mode(self, tinfo):
    if tinfo.info.name.endswith(('db/utool.txz', 'format/uk.txz')):
      return ReqMode.PROCESS
    elif tinfo.info.name.endswith('.txz'):
      return ReqMode.SKIP
    elif tinfo.is_archive():
      return ReqMode.SKIP
    elif tinfo.name == 'db/utool.txz':
      return ReqMode.NAMES if tinfo.info.name == 'ref.mxu' else ReqMode.SKIP
    elif tinfo.name == 'format/uk.txz':
      return ReqMode.NAMES
    return super().is_mode(tinfo)
       
# Exception raised when an entity is already present on the database
class FormatEntityExists(FileExistsError):
  pass

# Exception raised when there is an error within the data for an entity
class FormatEntityError(SqlSupportError):
  pass

# Exception raised for an error encountered by the SQL support objects
class FormatDatabaseError(SqlSupportError):
  pass

# Class providing state information required by several types of format entity
class FormatState(Namespace):
  def __init__(self, enttype):
    'Initialiase according to the ENTTYPE'
    super().__init__(enttype=enttype, state=0)
    """TODO: Possibly implement this fully:
    match enttype:
      case EntityType.FORMAT:
        self.
    """
  
  def update(self, **kwds):
    'Update according keeping the current enttype and state'
    kwds.pop('state', None)
    kwds.pop('enttype', None)
    super().update(kwds)

  def new_counter(self, name):
    self.name = itertools.count()

  def next(self, name):
    return next(self.name)


def read_help(fd, num):
  'Read the next NUM lines from the given FD as single string'
  match num:
    case 1:
      return unpack('%l', fd, True)
    case 2:
      return ' '.join((unpack('%l', fd, True), unpack('%l', fd, True)))
    case 0:
      return None
    case _:
      raise FormatEntityError(f'Invalid number of help lines given: {num}')

class FormatDatabase(SqlSupport):
  def __init__(self, dbname, debug=False):
    SqlSupport.__init__(self, dbname, debug=debug)
    self.prepare_tables()
    self.load_enttype()
    
  def load_message(self, unload, msgtyp='E', lang='uk'):
    'Load title messages from REF.MXU'
    if hasattr(self, 'message'):
      raise Warning('Messages have already been loaded')
    self.message = Message(unload, msgtyp=msgtyp, lang=lang, lnsep=' ')

  def lookup_message(self, msgcode):
    'Lookup title message if loaded'
    if hasattr(self, 'message'):
      return self.message.get(msgcode, None)
    raise ValueError('Messages have not been loaded')

  def load_component(self, unload):
    'Load valid components from DECOMP.MXU'
    self.component = set()

  def prepare_tables(self):
    'Prepare the database tables'
    self.create_table('enttype', 'type', type=int, usage=str)
    self.create_table('flagtype', ('type', 'entname', 'value'), type=int, entname=str, value=int, name=str)
    self.create_table('control', 'entity', entity=str, type=int, title=str, alias=str)
    self.create_table('format', 'entity', entity=str, numalt=int, hpos=int, vpos=int, width=int, depth=int, repeat=int, clear=int, confirm=int, overlap=int)
    self.create_table('field', ('entity', 'seq'), entity=str, seq=int, name=str, fldtype=int, fldlen=int, help=str, valtab=str, hpos=int, vpos=int, promptseq=int,
                      fldgroup=int, defvalue=str, decimals=int, inpmode=int, signed=int, zeros=int, convert=int, showhelp=int, wholenum=int, standout=int) #, onalt=int)
    # self.create_table('alternate', ('entity', 'altnum', 'seq'), entity=str, altnum=int, seq=int,  ...)
    self.create_table('window', 'entity', entity=str, hpos=int, vpos=int, width=int, depth=int, standout=int)
    self.create_table('barmenu', 'entity', entity=str, hpos=int, vpos=int, timeout=int, wipe=int, accept=int)
    self.create_table('baritem', ('entity', 'seq'), entity=str, seq=int, option=str, help=str, submenu=str, security=str, flag=int)
    self.create_table('popmenu', 'entity', entity=str, hpos=int, vpos=int, wipe=int, accept=int)
    self.create_table('popitem', ('entity', 'seq'), entity=str, seq=int, option=str, help=str, submenu=str, security=str, standout=int, flag=int)
    self.create_table('valtab', 'entity', entity=str, flag=int, extlen=int, intlen=int, desclen=int, defent=int)
    self.create_table('valitem', ('entity', 'seq'), entity=str, seq=int, external=str, internal=str, desc=str)
    # self.create_table('mask', 'entity', entity=str, nomatch=bool, ...)
    # self.create_table('maskalt', 'entity,seq', entity=str, seq=int, regexp=int, match=str, ...)
    # self.create_table('maskseg', 'entity,seq', entity=str, seq=int, type=int, numseq=int, ...flag=int)
    self.create_table('fixtext', ('entity', 'altnum', 'seq'), entity=str, altnum=int, seq=int, hpos=int, vpos=int, data=str)
    self.create_table('fixbox', ('entity', 'altnum', 'seq'), entity=str, altnum=int, seq=int, shpos=int, svpos=int, ehpos=int, evpos=int, standout=int)

  def load_enttype(self):
    if self.select_limit('enttype', 'type', 1) is None:
      for val in EntityType:
        self.insert('enttype', {'type': val.value, 'usage': val.name})
    if self.select_limit('flagtype', 'type', 1) is None:
      for info, dbname, enttype in all_flags:
        for name, value in info.__members__.items():
          self.insert('flagtype', {'type': enttype.value, 'entname': dbname, 'value': value, 'name': name})
    self.commit()

  def entity_exists(self, entname):
    'Check if entname already present on control table'
    return self.select('control', columns='type', where={'entity': entname}, limit=1) is not None

  def add_control(self, entname, enttype, title=None, alias=None):
    'Insert a control table entry for entity, if it is already present an exception will be raised'
    if title is None:
      title = self.lookup_message(entname)
    self.insert('control', {'entity': entname, 'type': enttype, 'title': title, 'alias': alias})
    
  # NOTE: Add a single method to handle the combined fixed text and box information updating the
  # NOTE: appropriate state information as necessary.
  _fixtext_re = re.compile(r'^\(\d+,(\d+),\d+\)$')
  def _add_fixtext(self, entname, altnum, seq, vpos, data):
    '''Add fixed text for alternate NUMALT, where 0 is main format,
    using the provided SEQ counter and VPOS with DATA'''
    line = unpack('%l', fd, True)
    rec = line.strip()
    if rec:
      self.insert('fixtext', {
        'entity': entname,
        'altnum': altnum,
        'seq': next(seq),
        'hpos': line.find(rec),
        'vpos': vpos,
        'data': rec,
      })
    
  _fixbox_re = re.compile(rb'^(L|B)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+|N)$')
  def _add_fixbox(self, entname, altnum, seq, data):
    '''Add a fixed box or line for alternate NUMALT, where 0 is main format,
    using the provided DATA and SEQ counter'''
    if m := self._fixbox_re.match(data):
      self.insert('fixbox', {
        'entity': entname,
        'altnum': altnum, 
        'seq': next(seq),
        'shpos': int(m.group(2)),
        'svpos': int(m.group(3)),
        'ehpos': int(m.group(4)),
        'evpos': None if m.group(1) == 'B' else int(m.group(5)),
        'standout': None if m.group(6) == 'N' else int(m.group(6)),
      })
    
  def add_format(self, fd, entname):
    'Parse and add a format entity to the database'
    # This method uses the following states:
    # 0 -> 1    : Handle the format header
    # 1 -> 2    : Handle the optional format fields, ends with an empty line
    # 2 -> 3,4  : Handle the fixed text definition line
    # 3 -> 4    : Handle the optional fixed text for the format
    # 4 -> None : Handle the optional line and boxes
    # NEW: state = FormatState(EntityType.FORMAT)
    state = 0
    for data in fd:
      match state.state:
        case 0:           # Handle the header for the format
          hdr = unpack_dict('{3d:hpos}{3d:vpos}{3d:width}{3d:depth}{f:clear}{3d:repeat}{c:rsense}{f:confirm}{d:numalt}{f:overlap}', data)
          try:
            # Add the format control information
            self.add_control(entname, EntityType.FORMAT)
            dbdata = {'entity': entname, 'numalt': 0,}
            dbdata.update(hdr)
            dbdata['repeat'] = LegacyFormatRepeat(hdr.repeat, hdr.rsense)
            if self._debug:
              print('Format:', entname)
            self.insert('format', dbdata)
          except FormatEntityExists:
            return
          state, numfld = 1, itertools.count()

        case 1:            # Handle fields for the format
          if data == b'\n':
            state = 2
          else:
            fld = unpack_dict('{9s:fldname}#{7*}{d:numhelp}{c:fldtype}{2d:numdec}{3d:fldsize}{3d:strsize}'
                              '{c:strtype}{3d:hpos}{3d:vpos}{2c:standout;inmode}{10s:valtab}{2c:signed;zeros}'
                              '{*}{2c:convert;showhelp}{10s:fldgroup}{10s:defval}{2c:wholenum;onalt}{*}'
                              '{3d:pmtseq}{c:deftyp}', data)
            fldtype = LegacyFieldType(fld.fldtype)
            if fldtype in (EntityFieldType.ALPHA, EntityFieldType.ALPHANUM, EntityFieldType.TEXT):
              fldlen = fld.strsize
            else:
              fldlen = None
            self.insert('field', {
              'entity': entname,
              'seq': next(numfld),
              'name': fld.fldname,
              'fldtype': fldtype,
              'fldlen': fldlen,
              'help': read_help(fd, fld.numhelp),
              'valtab': None if not fld.valtab or fld.valtab[0] == 'N' else fld.valtab,
              'hpos': fld.hpos,
              'vpos': fld.vpos,
              'promptseq': fld.pmtseq,
              'fldgroup': fld.fldgroup if fld.fldgroup else None,
              'defvalue': fld.defval if fld.defval else None,
              'decimals': fld.numdec,
              'inpmode': LegacyFieldMode(fld.inmode),
              'signed': LegacyFieldOption(fld.signed, fldtype),
              'zeros': LegacyFieldZeros(fld.zeros),
              'convert': LegacyFieldCase(fld.convert),
              'showhelp': False if fld.showhelp in ' N' else True,
              'wholenum': False if fld.wholenum in ' N' else True,
              'standout': False if fld.standout in ' N' else int(fld.standout),
            })

        case 2:            # Handle fixed text header for the format
          # Check for fixed text header
          if m := self._fixtext_re(data):
            state, vpos, numfix, seqfix = 3, 0, int(m.group(1)), itertools.count() # OLD
            # NEW: state, numfix, vpos, seqfix = 3, 0, int(data[1:-2].split(b',')[1]), itertools.count(), itertools.count()
          else:
            state, seqfix = 4, itertools.count()
              
        case 3:            # Handle fixed text lines
          # NEW: if not self._add_fixtext(entname, 0, seqfix, next(vpos), numfix, data):
          # NEW:   state, seqfix = 4, itertools.count()
          # NEW:   self._add_fixbox(entname, 0, seqfix, data)
          if vpos == numfix
            state, seqfix = 4, itertools.count()
            self._add_fixbox(entname, 0, seqfix, data)
          else:
            # Handle fixed text line
            line = unpack('%l', fd, True)
            rec = line.strip()
            if rec:
              self.insert('fixtext', {
                'entity': entname,
                'altnum': 0,
                'seq': next(seqfix),
                'hpos': line.find(rec),
                'vpos': vpos,
                'data': rec,
              })
            vpos += 1

        case 4:            # Handle fixed lines or boxes
          self._add_fixbox(entname, 0, seqfix, data)

    self.commit()

  def add_alternate(self, fd, entname, alt):
    'Parse and add a non-empty alternate to an existing format'
    # This method uses the following states:
    # BEGIN -> 1   : Handle the optional format fields, ends with an empty line
    state = 0
    for data in fd:
      match state:
        case 0:            # Handle the header information
          fld = unpack_dict('{9s:fldname}#{8*}{c:fldtype}{2d:numdec}{3d:fldsize}{3d:strsize}{c:strtype}{3d:hpos}{3d:vpos}{2c:standout;inmode}{10s:valtab}{2c:signed;zeros}{*}{2c:convert;showhelp}{10s:fldgroup}{10s:defval}{2c:wholenum;onalt}{*}{3d:pmtseq}{c:deftyp}', data)
          fldtype = LegacyFieldType(fld.fldtype)
          if fldtype in (EntityFieldType.ALPHA, EntityFieldType.ALPHANUM, EntityFieldType.TEXT):
            fldlen = fld.strsize
          else:
            fldlen = None
          self.insert('field', {
            'entity': entname,
            'seq': next(numfld),
            'name': fld.fldname,
            'fldtype': fldtype,
            'fldlen': fldlen,
            'help': read_help(fd, fld.numhelp),
            'valtab': None if not fld.valtab or fld.valtab[0] == 'N' else fld.valtab,
            'hpos': fld.hpos,
            'vpos': fld.vpos,
            'promptseq': fld.pmtseq,
            'fldgroup': fld.fldgroup if fld.fldgroup else None,
            'defvalue': fld.defval if fld.defval else None,
            'decimals': fld.numdec,
            'inpmode': LegacyFieldMode(fld.inmode),
            'signed': LegacyFieldOption(fld.signed, fldtype),
            'zeros': LegacyFieldZeros(fld.zeros),
            'convert': LegacyFieldCase(fld.convert),
            'showhelp': False if fld.showhelp in ' N' else True,
            'wholenum': False if fld.wholenum in ' N' else True,
            'standout': False if fld.standout in ' N' else int(fld.standout),
            # 'onalt': None if fld.onalt == 'N' else int(fld.onalt)
          })
    raise NotImplementedError('Format alternate')
  
  def add_window(self, fd, entname):
    'Parse and add a window entity to the database'
    wininfo = unpack_dict('{3d:hpos}{3d:vpos}{3d:width}{3d:depth}{2d:fgstand}{12*}', fd)
    try:
      self.add_control(entname, EntityType.WINDOW, title=self.message.get(entname, None))
      if self._debug:
        print('Window:', entname)
      dbdata = {'entity': entname, 'standout': None if wininfo.fgstand == 8 else int(wininfo.fgstand)}
      dbdata.update(wininfo)
      self.insert('window', dbdata)
    except FormatEntityExists:
      return
    self.commit()

  def add_menu(self, fd, entname):
    'Parse either a barmenu or popmenu according to the second line'
    info = unpack_dict('{c:typ}{3d:hpos}{2d:vpos}{c:msg}{8*}{2f:wipe;accept}', fd)
    match info.typ:
      case 'P':
        self._add_popmenu(fd, entname, info)
      case 'B':
        self._add_barmenu(fd, entname, info)
      case _:
        raise FormatEntityError(f'UNHANDLED: {info}')
    self.commit()
      
  def _add_popmenu(self, fd, entname, info):
    'Parse and add a popmenu entity to the database'
    self.add_control(entname, EntityType.POPMENU, read_help(fd, 1))
    dbdata = {'entity': entname,}
    dbdata.update(info)
    self.insert('popmenu', dbdata)
    numseq = itertools.count()
    for data in fd:
      item = unpack_dict('{40s:text}{9s:submenu}{3c:option;standout;retcode}#{7*}{d:numhelp}{3c:disabled;secgrp;seclev}', data)
      self.insert('popitem', {
        'entity': entname,
        'seq': next(numseq),
        'option': item.option if item.option == item.retcode else f'{item.option}{item.retcode}',
        'help': read_help(fd, item.numhelp),
        'submenu': None if item.submenu == '' else item.submenu,
        'security': None if item.secgrp == ' ' and item.seclev == ' ' else f'{item.secgrp}{item.seclev}',
        'standout': None if item.standout == 'N' else item.standout, 
        'flag': item.disabled,
      })

  def _add_barmenu(self, fd, entname, info):
    'Parse and add a popmenu entity to the database'
    self.add_control(entname, EntityType.BARMENU, read_help(fd, 1))
    dbdata = {'entity': entname, 'timeout': None}
    dbdata.update(info)
    self.insert('barmenu', dbdata)
    numseq = itertools.count()
    for data in fd:
      try:
        item = unpack_dict('{40s:text}{9s:submenu}{c:option}{*}{c:retcode}#{7*}{d:numhelp}{f:disabled}{2c:secgrp;seclev}', data)
        self.insert('baritem', {
          'entity': entname,
          'seq': next(numseq),
          'option': item.option if item.option == item.retcode else f'{item.option}{item.retcode}',
          'help': read_help(fd, item.numhelp),
          'submenu': None if item.submenu == '' else item.submenu,
          'security': None if item.secgrp == ' ' and item.seclev == ' ' else f'{item.secgrp}{item.seclev}',
          'flag': item.disabled,
        })
      except UnpackError:
        item = unpack_dict('{40s:timeout}{9*}. .{11*}', data)
        self.update('barmenu', {'timeout': int(item.timeout)}, {'entity': entname})

  def add_valtab(self, fd, entname):
    'Parse and add a validation table to the database'
    # TODO: Handle validation tables with simply a sequence of one-to-one mappings
    # This methods uses the following states:
    # BEGIN -> 1    : Handle the validation table header
    # 1     -> END  : Handle the validation table entries
    state = 0
    for num, data in enumerate(fd):
      match state:
        case 0:       # Handle the header for the validation table
          info = unpack_dict('{f:editable}{2d:extlen}{2d:intlen}{2d:desclen}{4d:defent}{2f:blank;search}{c:type}{4*:nument}', data)
          info.defent = None if info.defent == 0 else info.defent - 1
          flag = 1 if info.search else 0
          flag |= 2 if info.blank else 0
          flag |= 4 if info.editable else 0
          self.add_control(entname, EntityType.VALTAB)
          dbdata = {'entity': entname, 'flag': flag}
          dbdata.update(info)
          self.insert('valtab', dbdata)      # NEW
          if info.desclen:
            itemfmt = f'{{{info.intlen}s:internal}}{{{info.extlen}s:external}}{{{info.desclen}s:desc}}'
          else:
            itemfmt = f'{{{info.intlen}s:internal}}{{{info.extlen}s:external}}'
          state, numseq = 1, itertools.count()
          
        case 1:       # Handle the items for the validation table
          item = unpack_dict(itemfmt, data)
          dbdata = {'entity': entname, 'seq': next(numseq)}
          dbdata.update(item)
          if not info.desclen:
            dbdata['desc'] = None
          self.insert('valitem', dbdata)

    self.commit()

  def add_mask(self, fd, entname):
    'Parse and add a mask to the database'
    nomatch = unpack('%d', fd)[0]
    data, altseq, seq = fd.readline(), 0, 0
    while data:
      if data.startswith(b'A'):
        # Add a new alternate
        regexp, regpatt = unpack('A%d%s', data)
        # TODO: Finish implementation

      else:
        # Add a new seqment
        maskseq = unpack_dict('{2f:optin;redisp}{d:type}{2d:numseq}{%2d:numname}{2d:fixlen}'
                              '{2f:varlen;collapse}{2c:chrfill;chrtype}{d:numdec}'
                              '{3f:vardec;dispzero;spaced}{s:values}', data)
        flag = 1 if maskseq.optin else 0
        flag |= 2 if maskseq.redisp else 0
        flag |= 4 if maskseq.varlen else 0
        flag |= 8 if maskseq.collapse else 0
        flag |= 16 if maskseq.vardec else 0
        flag |= 32 if maskseq.dispzero else 0
        flag |= 64 if maskseq.spaced else 0

    raise NotImplementedError('Mask')

def main(dbname='uk_format.db'):
  tfpath = f'{os.path.dirname(__file__)}/1404002.tar'
  tf = FormatArchive(tfpath, 'uk')
  db = FormatDatabase(dbname)
  dfd = open('bad_formats.lst', 'wt')
  
  # Skip until required subarchive
  for ti in iter(tf):
    if ti.name.endswith('format/uk.txz') and not ti.info.isdir():
      # Handle formats
      entname = os.path.basename(ti.info.name)
      if not db.entity_exists(entname):
        with ti.open() as fd:
          try:
            enttype = unpack('010105%c', fd)[0]
          except UnpackError:
            print('UNPACK:', ti.info.name, file=dfd)
            continue
          try:
            match enttype:
              case '0':
                # Format
                db.add_format(fd, entname)
              case '1'|'2'|'3'|'4'|'5'|'6'|'7'|'8'|'9':
                # Format alternate
                pass # TODO: db.add_altermate(fd, entname, enttype - ord('0'))
              case 'A':
                # Popmenu or Barmenu
                db.add_menu(fd, entname)
              case 'M':
                # Mask
                pass # TODO: db.add_mask(fd, entname)
              case 'V':
                # Validation table
                db.add_valtab(fd, entname)
              case 'W':
                # Window
                db.add_window(fd, entname)
              case _:
                raise ValueError(f'Unhandled screen entity: {enttype}')
          except:
            print('ERROR:', entname)
            raise               
    elif ti.name.endswith('db/utool.txz'):
      # Handle utool database
      if ti.info.name.endswith('ref.mxu'):
        # Load messages from the REF file
        with ti.open() as fd:
          db.load_message(fd.read().decode('iso8859-1'))

  
if __name__ == '__main__':
  main()
