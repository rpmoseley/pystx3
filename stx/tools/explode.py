'''
This is a python re-implementation of the deexpl() function using a more
efficient implementation that performs the expansion using a insert-sort
rather than writing to a file, then sorting it, then reading it in.
'''

import dataclasses
import heapq
from typing import Sequence

@dataclasses.dataclass
class ExplodeItem:
  comp: str
  ctyp: str
  seq: int = 0

class ExplodeList:
  '''Class that inserts new elements that aren't already present in 
     pre-sorted order that is ascending according to the specified
     comparison method'''
  def __init__(self, initval=None, debug=True):
    self._list = list()              # Initialise the list object
    self._seen = set()
    self._debug = debug
    if isinstance(initval, ExplodeItem):
      self._list.append(initval)
    elif isinstance(initval, Sequence):
      self._list.extend(initval)
    elif initval:
      self._list.append(ExplodeItem(initval))
    
    # Turn list into heap
    heapq.heapify(self._list)
      
  def add(self, item):
    if isinstance(item, ExplodeItem):
      heapq.heappush(self._list, item)
    elif isinstance(item, Sequence):
      for i in item:
        self.add(i)
    elif item:
      heapq.heappush(self._list, ExplodeItem(item))

    
class Explode:
  'Class representing the explosion of an item from a backend database'
  def __init__(self, basecomp=None, dbconn=None):
    self._inslist = ExplodeList(basecomp)
    

def test_list_1():
  
if __name__ == '__main__':
  pass
