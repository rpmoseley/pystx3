'''
Variant providing a socketpair based interface replacing the pipe originally used.
'''

import os
import resource
import socket

class CommWire:
  def open(self, appl, resfd=None, env=None, *args):
    # Ensure that channel 3 is available for the child process
    fds = socket.socketpair()
    pid = os.fork()
    if pid:
      # Parent part of fork
      self.appl = appl
      os.close(fds[1])
      self._pid = pid
      self._sfd = fds[0]
    else:
      # Child part of fork
      os.dup2(3, fds[1])
      os.closerange(4, resource.getrlimit(resource.RLIMIT_NOFILE)[0])
      os.execve(appl, args, env)

  def close(self):
    self._sfd.close()
    self._sfd = None

  def read(self, numbyte):
    return self._sfd.read(numbyte)

  def write(self, byteval):
    if isinstance(byteval, str):
      self._sfd.write(byteval.encode('iso8859-1'))
    else:
      self._sfd.write(byteval)
