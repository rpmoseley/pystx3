'''
Implements the raw byte transfer that was used in the original software.
'''

from .common import CommMixin

class Comm(CommMixin):
  def __init__(self, appl, resfd=None, env=None, *args):
    CommMixin.__init__(self, appl, resfd, env, *args)
    
  def recv_compress(self):
    match self.recv_char():
      case 'U':
        return self.recv_record()
      case 'C':
        data, count = bytearray(), 0
        dsize, cdata = self.recv_short(), self.recv_record()
        csize = len(cdata) if cdata else 0
        while count < csize:
          if cdata[count] & 0x80:
            data.extend(cdata[count-1] * (cdata[count] & 0x7f))
            count += 2
          else:
            data.append(cdata[count])
            count += 1
        else:
          if len(data) != dsize:
            raise ValueError('Uncompressed size not expected size')
      case _:
        raise ValueError('Unknown compression method')
    return data

  def send_compress(self, val):
    udata = val.encode('iso8859-1') if isinstance(val, str) else val
    usize = len(udata)
    cdata = bytearray()
    count = rsize = 0
    while count < usize:
      byt = udata[count]
      count += 1
      if count < usize and udata[count] == byt:
        rsize = 2
        count += 1
      while count < usize and udata[count] == byt and rsize < 0x7f:
        rsize += 1
        count += 1
      cdata.append(rsize | 0x80)
      cdata.append(byt)
    csize = len(cdata)
    if csize < usize:
      self.send_char('C')
      self.send_short(usize)
      self.send_record(cdata)
    else:
      self.send_char('U')
      self.send_record(udata)
