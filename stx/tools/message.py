'''
This module will provide all the messages found on the REF table for use when there is
no database existing during bootstrap or installation.
'''

import dataclasses

@dataclasses.dataclass
class PrevMessage:
  code: str
  mess: list[str] = dataclasses.field(default_factory=list)

@dataclasses.dataclass
class RefMXU:
  lang: str
  prefix: str
  code: str
  text: str

class Message:
  '''Class that will provide the lookup of uk messages'''
  def __init__(self, unload, msgtyp='E', lang='uk', lnsep='\n'):
    if not isinstance(unload, str):
      raise TypeError('Pass the pre-processed unload data as a single string')
    self._msg = dict()
    self.read_unload(unload.splitlines(), msgtyp, lang, lnsep)

  def __getitem__(self, code):
    return self._msg[code]

  def get(self, code, default):
    return self._msg.get(code, default)
  
  def read_unload(self, unload, msgtyp, lang, lnsep, sep='|'):
    prev, row_check = None, f'{lang}{sep}{msgtyp}{sep}'
    for row in unload:
      if row.startswith(row_check):
        try:
          flds = row.split(sep)
          rec = RefMXU(flds[0], flds[1], flds[2], flds[5])
          if rec.lang == lang and rec.prefix == msgtyp:
            if rec.code.isalnum():
              if prev is None:
                prev = PrevMessage(rec.code)
              elif rec.code != prev.code:
                self._msg[prev.code] = lnsep.join(prev.mess)
                prev = PrevMessage(rec.code)
              if not (rec.text[0].isspace() or rec.text.startswith('Created on')):
                prev.mess.append(rec.text)
          elif self._msg:
            break
        except IndexError:
          if prev:
            self._msg[prev.code] = lnsep.join(prev.mess)
            prev = None
    else:
      if prev:
        self._msg[prev.code] = lnsep.join(prev.mess)

if __name__ == '__main__':
  ref_data = open('extarch/ref_uk.mxu', 'rt', encoding='iso8859-1').read()
  ## ref_data = 'uk|E|adco0|0|0|User Maintenance for Strategix|N| | |\nuk|E|ref|0|0|Messages File|N| | |\nuk|E|zztest|0|0|test|N| | |\nuk|E|zztest|1|0|Created on Mon 15 Feb 1993 at 04:55:02 PM by g2cr|N| | |\n'
  m = Message(ref_data)
  print(m['ref'])
  print(m['adco0'])
  print(m['zztest'])
