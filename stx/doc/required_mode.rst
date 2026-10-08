This file outlines the reasoning for the handling of the modes of members within an archive,
which contains further sub-archives, recursively. It is meant to be used in combination with the
Archive class which processes a given archive, processing sub-archives as they are encountered,
and requires another helper class to perform the non-trival lookup of member modes, handling 
varies situations where both a common mode should be given, as well as the non-common mode for
particular members within the same archive. This should also enable a user module to state what
members it wants to retrieve, with all others being skipped without yielding a single value.

The RequiredMode class
======================
This class provides the necessary functionality to give the correct mode, based on the member
within the current archive, defaulting back to a suitable default.



Example usage of the RequiredMode
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The following is an example, taken from a real use, from the pystx package, and is found in the
createfmtdb module, where messages are taken from the unload data for a database table, together
with a complete directory tree for the formats in a particular language. The formats and database
are stored within different archives within the main one.

rq = RequiredMode(dirmode=ReqMode.SKIP, filemode=ReqMode.SKIP)
rq.add('db/utool', 'ref.mxu', ReqMode.FILEOBJ)
rq.add('format/uk', None, ReqMode.FILEOBJ)

This should produce a mapping as follows:

rq._map =         (ReqMode.SKIP, ReqMode.SKIP, {           # mm1
  'db':           (ReqMode.SKIP, ReqMode.SKIP, {           # mm2
    'utool':      (ReqMode.SKIP, ReqMode.SKIP, {           # mm3
       'ref.mxu': ReqMode.FILEOBJ,                         # mm4
    }),
  }),
  'format':       (ReqMode.SKIP, ReqMode.SKIP, {           # mm5
    'uk':         ReqMode.FILEOBJ,                         # mm6
  }),
})

This means that each entry in a mode mapping can consists of the following:

ent ::= ModeMapItem|ReqMode

Example made into a module:

import dataclasses
import enum

class ReqMode(enum.IntEnum):
  SKIP = 0
  PROCESS = 1
  FILEOBJ = 2
  EXTRACT = 3
  NAMES = 4

@dataclasses.dataclass
class ModeMapItem:
  memb: ReqMode 
  dirs: ReqMode = ReqMode.SKIP
  arch: dict[str,'ModeMapItem']|None = None

class Required:
  def __init__(self, memb: ReqMode=ReqMode.SKIP, dirs: ReqMode=ReqMode.SKIP) -> None:
  def add(self, path: str|None, memb: str|list[str]|tuple[str]|None, mode: ReqMode) -> None:

The following is the expected lifetime of the use of a Required class in a typical module:

1. Create an empty object using the default values.
   rq = Required()
   -> rq._map = ModeMapItem(ReqMode.SKIP, ReqMode.SKIP, None)

2. Add a default for non-archive members.
   rq.add(None, None, ReqMode.NAMES)
   -> rq._map = ModeMapItem(ReqMode.NAMES, ReqMode.SKIP, None)


