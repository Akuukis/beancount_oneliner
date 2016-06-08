__author__ = 'Akuukis <akuukis@kalvis.lv'
__plugins__ = ['beanoneliner']

import sys

from beancount.core.amount import Amount, mul
from beancount.core import data
from beancount.core.number import D

def beanoneliner(entries, options_map, config):
  """Parse note oneliners into valid transactions. For example,
  1999-12-31 note Assets:Cash "Income:Test -16.18 EUR * Description goes here *"""

  errors = []

  new_entries = []

  for entry in entries:
    if(isinstance(entry, data.Note) and entry.comment[-1:] == "*"):
      try:
        p1 = data.Posting(account=entry.comment.split()[0],
                  units=Amount.from_string(' '.join(entry.comment.split()[1:3])),
                  cost=None,  # TODO
                  price=None,  # TODO
                  flag=None,
                  meta=None)
        p2 = data.Posting(account=entry.account,
                  units=mul(Amount.from_string(' '.join(entry.comment.split()[1:3])), D(-1)),
                  cost=None,
                  price=None,
                  flag=None,
                  meta=None)
        e = data.Transaction(date=entry.date,
                   meta=entry.meta,
                   flag=entry.comment.split()[3],
                   payee=None,  # TODO
                   narration=' '.join(entry.comment.split()[4:-1]),
                   tags={'NoteToTx'},
                   links=None,  # TODO
                   postings=[p1, p2])
        new_entries.append(e)
        # print(e)
      except:
        print(entry, sys.exc_info())
    else:
      new_entries.append(entry)

  return new_entries, errors
