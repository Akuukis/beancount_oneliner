"""Write your simple transactions on one line."""
__author__ = "Akuukis <akuukis@kalvis.lv"
__plugins__ = ["oneliner"]

import sys
import re

from collections import namedtuple
from beancount.core.amount import Amount, mul
from beancount.core import data
from beancount.core.position import Cost
from beancount.core.number import D
from beancount.core.number import ONE
from beancount.core.number import ZERO
from beancount.core.data import EMPTY_SET, new_metadata
from beancount.core import interpolate
from beancount.utils import defdict

RE_COST = re.compile(r"\{(.*)\}")
RE_PRICE = re.compile(r"\ \@(.*?)\*")
RE_TAG = re.compile(r"(?<=\s)(#)([A-Za-z0-9\-_/@.]+)")


PluginOnelinerParseError = namedtuple("LoadError", "source message entry")


# Good to remember that beancount passes these parameters to all plugins.
# pylint: disable=unused-argument
def oneliner(entries, options_map, config):
    """Parse note oneliners into valid transactions. For example,
    1999-12-31 note Assets:Cash "Income:Test -16.18 EUR * Payee | Description goes here *"
    """

    errors = []

    new_entries = []

    for entry in entries:
        # data.* are custom types, I think.
        # pylint: disable=isinstance-second-argument-not-valid-type
        if isinstance(entry, data.Note) and entry.comment[-1:] == "*":
            comment = entry.comment
            try:
                k = None
                maybe_cost = RE_COST.findall(comment)
                if len(maybe_cost) > 0:
                    amount = maybe_cost[0].split()[0]
                    currency = maybe_cost[0].split()[1]
                    cost = Cost(D(amount), currency, None, None)
                    k = mul(cost, D(-1))
                    comment = RE_COST.sub("", comment)
                else:
                    cost = None

                maybe_price = RE_PRICE.findall(comment)
                if len(maybe_price) > 0:
                    price = Amount.from_string(maybe_price[0])
                    k = k or mul(price, D(-1))
                    comment = RE_PRICE.sub("", comment)
                else:
                    price = None

                comment_tuple = comment.split()
                other_account = comment_tuple[0]
                units = Amount.from_string(" ".join(comment_tuple[1:3]))
                flag = comment_tuple[3]
                narration_tmp = " ".join(comment_tuple[4:-1])
                tags = {"NoteToTx"}
                for tag in RE_TAG.findall(narration_tmp):
                    tags.add(tag[1])
                tags = frozenset(tags)
                narration = RE_TAG.sub("", narration_tmp).rstrip()

                k = k or Amount(D(-1), units.currency)

                # print(type(cost), cost, type(price), price, type(units), units, k, comment)
                p1 = data.Posting(
                    account=other_account,
                    units=units,
                    cost=cost,
                    price=price,
                    flag=None,
                    meta={
                        "filename": entry.meta["filename"],
                        "lineno": entry.meta["lineno"],
                    },
                )
                p2 = data.Posting(
                    account=entry.account,
                    units=mul(k, units.number),
                    cost=cost,
                    price=None,
                    flag=None,
                    meta={
                        "filename": entry.meta["filename"],
                        "lineno": entry.meta["lineno"],
                    },
                )
                e = data.Transaction(
                    date=entry.date,
                    flag=flag,
                    payee=None,  # TODO
                    narration=narration,
                    tags=tags,  # TODO
                    links=EMPTY_SET,  # TODO
                    postings=[p1, p2],
                    meta=entry.meta,
                )

                # Get the AUTOMATIC_TOLERANCES meta that all transaction should have.
                # This is a simplified extraction from `infer_tolerances` function within beancount.
                tolerances = options_map["inferred_tolerance_default"].copy()
                expo = units.number.as_tuple().exponent
                tolerances[units.currency] = ONE.scaleb(expo) * options_map["inferred_tolerance_multiplier"]
                default = tolerances.pop("*", ZERO)
                meta = e.meta.copy()
                meta[interpolate.AUTOMATIC_TOLERANCES] = defdict.ImmutableDictWithDefault(tolerances, default=default)
                e = e._replace(meta=meta)

                new_entries.append(e)
                # print(e)
            # I'm not sure what else to except.
            # pylint: disable=broad-exception-caught
            except Exception as e:
                print("beancount_oneliner error:", entry, sys.exc_info())
                errors.append(
                    PluginOnelinerParseError(
                        new_metadata(entry.meta["filename"], entry.meta["lineno"]),
                        "PluginOneliner: " + str(e),
                        entry,
                    )
                )
                new_entries.append(entry)
                continue
        else:
            new_entries.append(entry)

    return new_entries, errors
