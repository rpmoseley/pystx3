'''
This module provides the shared enumerations used by the tools subpackage to avoid circular
dependancies.
'''

import enum

# List of required values
class ReqMode(enum.IntEnum):
  SKIP = 0
  PROCESS = 1
  FILEOBJ = 2
  EXTRACT = 3
  NAMES = 4
