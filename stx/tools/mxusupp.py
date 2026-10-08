'''
This module provides the creation of a dataclass for each table defined in the defile.mxu
file, and enables the rest of the package to access appropriately converted values from
other unload files.
'''

from dataclasses import dataclass, make_dataclass
try:
  from annotationlib import get_annotations
except ModuleNotFoundError:
  from inspect import get_annotations

@dataclass
class DefnInfo
  tabname: str
  begin: int
  end: int = 0

class TableDefn:
  'Class encapsulating the logic to return the definition of a table'
  _data = None           # Unloaded records
  _rows = None           # Ranges of each table within _data
  _defn = dict()         # Previously defined tables

  def __init__(self, mxufile: str|bytes|list|tuple) -> None:
    if self._data is None:
      if isinstance(mxufile, str):
        data = open(mxufile, 'rt').readlines()
      elif isinstance(mxufile, bytes): 
        data = mxufile.decode('iso8859-1').readlines()
      elif isinstance(mxufile, (tuple, list)):
        data = mxufile
      self._data = data
      rows = self._rows = dict()
      prev = None
      for off, line in enumerate(data):
        curr = self.fields(line, 0)
        if curr.startswith(' '):
            continue
        elif prev is None:
          prev = DefnInfo(curr, off)
        elif curr != prev.tabname:
          prev.end = off
          rows[prev.tabname] = prev
          prev = DefnInfo(curr, off)
      else:
        prev.end = -1
        rows[prev.tabname] = prev

  def __call__(self, tabname):
    try:
      tabmxu = self._defn[tabname]
    except KeyError:
      defn = list()
      rowrange = self._rows[tabname]
      for row in self._data[rowrange.begin:rowrange.end]:
        field, stype = self.fields(row, 2, 8)
        match int(stype) & 7:
          case 0:
            defn.append((field, str))
          case 1|2|3:
            defn.append((field, int))
          case 4|5:
            defn.append((field, float))
      tabmxu = self._defn[tabname] = make_dataclass(f'{tabname.capitalize()}MXU',
                                                    defn,
                                                    namespace=self._dc_ns)
    return tabmxu
 
  def fields(self, record, *reqd):
    flds = record.split('|')
    if len(reqd) == 1:
      return flds[reqd[0]]
    else:
      return tuple(flds[n] for n in reqd)

  @classmethod
  def load(cls, record, sep='|'):
    flds = record.split(sep) if isinstance(record, str) else record.decode('ascii').split(sep)
    args = tuple(c(flds[n]) for n, c in enumerate(get_annotations(cls).values()))
    return cls(*args)
  
  _dc_ns = {'load': load,}

if __name__ == '__main__':
    td = TableDefn(
