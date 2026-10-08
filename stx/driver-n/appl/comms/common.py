'''
Module containing the shared functionality of the application to driver interface.
'''

import os
import struct
from .wire import CommWire

_short = struct.Struct('H')
_int = struct.Struct('I')

class CommMixin(CommWire):
  def __init__(self, appl, resfd=None, env=None, *args):
    exec_env = os.environ.copy()
    if env:
      exec_env.update(env)
    if len(args) == 0:
      args = (appl,)
    self.open(appl, resfd, exec_env, *args)

  def receive(self, fmt):
    'Super method for receiving a sequence of values at once'
    fval = list()
    for fchr in fmt:
      match fchr:
        case 'c':         # Character
          fval.append(self.recv_char())
        case 'B':         # Boolean
          fval.append(self.recv_bool())
        case 'b':         # Byte (8bit)
          fval.append(self.recv_byte())
        case 'h':         # Short (16bit)
          fval.append(self.recv_short())
        case 'i':         # Integer (32bit)
          fval.append(self.recv_int())
        case 'l':         # Long (64bit)
          fval.append(self.recv_long())
        case 'r':         # Record
          fval.append(self.recv_record())
        case 's':         # String
          fval.append(self.recv_string())
        case 'z':         # Compressed
          fval.append(self.recv_compress())
        case 'V':         # Variable data follows
          fval.append(self.recv_variable())
        case _:
          raise ValueError(f'Unsupported: {fchr}')
    return fval 

  def send(self, fmt, *vals):
    'Super method for sending a sequence of values at once'
    assert len(fmt) == len(vals)
    for fchr, fval in zip(fmt, vals):
      match fchr:
        case 'c':         # Character
          self.send_char(fval)
        case 'B':         # Boolean
          self.send_bool(fval)
        case 'b':         # Byte (8bit)
          self.send_byte(fval)
        case 'h':         # Short (16bit)
          self.send_short(fval)
        case 'i':         # Integer (32bit)
          self.send_int(fval)
        case 'l':         # Long (64bit)
          self.send_long(fval)
        case 'r':         # Record
          self.send_record(fval)
        case 's':         # String
          self.send_string(fval)
        case 'z':         # Compressed
          self.send_compress(fval)
        case _:
          raise ValueError(f'Unsopported: {fchr}')

  def recv_byte(self):
    return self.read(1)[0]

  def recv_char(self):
    return self.read(1).decode('iso8859-1')

  def recv_bool(self):
    return self.read(1)[0] == '1'

  def recv_short(self):
    return _short.unpack(self.read(_short.size))[0]

  def recv_int(self):
    return _int.unpack(self.read(_int.size))[0]

  def recv_record(self):
    vlen = self.recv_short()
    return self.read(vlen) if vlen else None

  def recv_string(self):
    vlen = self.recv_short()
    return self.read(vlen).decode('iso8859-1')[:-1] if vlen else None

  def recv_variable(self):
    vchr = self.recv_char()
    match vchr:
      case 'C':           # Character follows
        return self.recv_char()
      case 'D':           # Double follows
        return self.recv_double()
      case 'L':           # Int follows
        return self.recv_int()
      case 'N':           # Nothing follows
        return None
      case 'R':           # Record follows
        return self.recv_record()
      case 'S':           # Short follows
        return self.recv_short()
      case 'T':           # String follows
        return self.recv_string()
      case _:
        raise ValueError(f'VDATA: {vchr}')

  def send_byte(self, val):
    self.write(val[0])

  def send_char(self, val):
    self.write(val[0].encode('iso8859-1') if isinstance(val, str) else val[0])

  def send_bool(self, val):
    self.write('1' if val else '0')

  def send_short(self, val):
    self.write(_short.pack(val))

  def send_int(self, val):
    self.write(_int.pack(val))

  def send_record(self, val):
    self.send_short(len(val))
    self.write(val)
    
  def send_string(self, val):
    self.send_short(len(val)+1)
    if val:
      self.write(val)
    self.write(0x00)
