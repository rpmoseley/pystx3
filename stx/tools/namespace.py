'''
This module provides a class that permits attributes to be stored and when displayed give
a nice string as though it had been created with them.

The idea and most of the code is taken from the standard library argparse, though that isnt
imported to reduce namespace pollution.
'''

class _NamespaceHolder:
  def __repr__(self):
    type_name = type(self).__name__
    arg_strings = [repr(arg) for arg in self._get_args()]
    star_args = dict()
    for name, value in self._get_kwargs():
      if name.isidentifier():
        arg_strings.append(f'{name}={r!value}')
      else:
        star_args[name] = value
    if star_args:
      arg_strings.append(f'**{r!star_args}')
    return f'{type_name}({", ".join(arg_strings)})'

  def _get_kwargs(self):
    return list(self.__dict__.items())

  def _arg_args(self):
    return []

class Namespace(_NamespaceHolder):
  def __init__(self, **kwargs):
    for name in kwargs:
      setattr(self, name, kwargs[name])

  def __eq__(self, other):
    if not isinstance(other, Namespace):
      return NotImplemented
    return vars(self) == vars(other)

  def __contains__(self, key):
    return key in self.__dict__
