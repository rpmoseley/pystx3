'''
Variant implementing original wire protocol where the application expected to receive
data on channel 3 and send on channel 4.
'''

import fcntl
import os
import resource

class CommWire:
  def open(self, appl, resfd=None, env=None, *args):
    # Ensure that channels 3 and 4 are available
    try:
      fcntl.fcntl(3, fcntl.F_GETFD)
      os.dup(3)
    except OSError:
      if os.open('/dev/null', os.O_RDONLY) != 3:
        raise ValueError('First available read channel not 3')
    try:
      fcntl.fcntl(4, fcntl.F_GETFD)
      os.dup(4)
    except OSError:
      if os.open('/dev/null', os.O_WRONLY) != 4:
        raise ValueError('First available write channel not 4')

    # Open the two pipes for communication
    pRc, pWc = os.pipe()
    cRp, cWp = os.pipe()

    # Create the child process
    pid = os.fork()
    if pid:
      # Parent
      self.appl = appl
      os.close(pWc)
      os.close(cRp)
      self._pid, self._rfd, self._wfd = pid, os.fdopen(pRc, 'rb'), os.fdopen(cWp, 'wb')
      self._flush = False
    else:
      # Child
      cRp = os.dup2(cRp, 3)
      pWc = os.dup2(pWc, 4)
      os.closerange(5, resource.getrlimit(resource.RLIMIT_NOFILE)[0])
      os.execve(appl, args, env)

  def close(self):
    self.flush()
    self._rfd.close()
    self._wfd.close()
    self._rfd = self._wfd = None

  def flush(self):
    if self._wfd and self._flush:
      self._wfd.flush()
      self._flush = False

  def read(self, numbyte):
    self.flush()
    return self._rfd.read(numbyte)

  def write(self, byteval):
    if isinstance(byteval, str):
      self._wfd.write(byteval.encode('iso8859-1'))
    elif isinstance(byteval, int):
      self._wfd.write(byteval.to_bytes())
    else:
      self._wfd.write(byteval)
    self._flush = True
