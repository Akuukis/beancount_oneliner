__author__ = 'Akuukis <akuukis@kalvis.lv'
__plugins__ = ['beanoneliner']

import sys, re

from beancount.core.amount import Amount, mul
from beancount.core import data
from beancount.core.position import Cost
from beancount.core.number import D

RE_COST = re.compile('\{(.*)\}')
RE_PRICE = re.compile('\@(.*)\*')

def beanoneliner(entries, options_map, config):
  """Parse note oneliners into valid transactions. For example,
  1999-12-31 note Assets:Cash "Income:Test -16.18 EUR * Description goes here *" """

  errors = []

  new_entries = []

  for entry in entries:
    if(isinstance(entry, data.Note) and entry.comment[-1:] == "*"):
      comment = entry.comment
      try:
        k = None
        maybe_cost = RE_COST.findall(comment)
        if len(maybe_cost) > 0:
          amount = maybe_cost[0].split()[0]
          currency = maybe_cost[0].split()[1]
          cost = Cost(D(amount), currency, None, None)
          k = mul(cost, D(-1))
          comment = RE_COST.sub('', comment)
        else:
          cost = None

        maybe_price = RE_PRICE.findall(comment)
        if len(maybe_price) > 0:
          price = Amount.from_string(maybe_price)
          k = k or mul(price, D(-1))
          comment = RE_PRICE.sub('', comment)
        else:
          price = None

        comment_tuple = comment.split()
        units = Amount.from_string(' '.join(comment_tuple[1:3]))
        k = k or Amount(D(-1), units.currency)

        # print(type(cost), cost, type(price), price, type(units), units, k, comment)
        p1 = data.Posting(account=comment_tuple[0],
                  units=units,
                  cost=cost,
                  price=price,
                  flag=None,
                  meta={'filename': entry.meta['filename'], 'lineno': entry.meta['lineno']})
        p2 = data.Posting(account=entry.account,
                  units=mul(k, units.number),
                  cost=None,
                  price=None,
                  flag=None,
                  meta={'filename': entry.meta['filename'], 'lineno': entry.meta['lineno']})
        e = data.Transaction(date=entry.date,
                   flag=comment_tuple[3],
                   payee=None,  # TODO
                   narration=' '.join(comment_tuple[4:-1]),
                   tags={'NoteToTx'},  # TODO
                   links=None,  # TODO
                   postings=[p1, p2],
                   meta=entry.meta)
        new_entries.append(e)
        # print(e)
      except:
        print(entry, sys.exc_info())
    else:
      new_entries.append(entry)

  return new_entries, errors
