'''
This module provides the common functionality inherieted by the various variants of handlers
'''

class ControlBase:
  def __init__(self):
    self._resume = False
    self._fxon = False
