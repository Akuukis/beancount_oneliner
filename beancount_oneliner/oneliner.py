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
RE_PRICE = re.compile(r"\ \@\s*?(.*?)(?=\ \*)")
RE_TAG = re.compile(r"(?<=\s)(#)([A-Za-z0-9\-_/@.]+)")
RE_LINK = re.compile(r"(?<=\s)(\^)([A-Za-z0-9\-_/@.]+)")
RE_PAYEE = re.compile(r"(.*?)\|")


def prefixHash(string):
    return "#" + string


def prefixCarrot(string):
    return "^" + string


PluginOnelinerParseError = namedtuple("LoadError", "source message entry")


def extract_optional_cost(comment: str):
    """Extract cost from comment if there's any."""
    maybe_cost = RE_COST.findall(comment)
    if len(maybe_cost) > 0:
        amount = maybe_cost[0].split()[0]
        currency = maybe_cost[0].split()[1]
        cost = Cost(D(amount), currency, None, None)
        comment = RE_COST.sub("", comment)
    else:
        cost = None

    return comment, cost


def extract_optional_price(comment: str):
    """Extract price from comment is there's any"""
    maybe_price = RE_PRICE.findall(comment)
    if len(maybe_price) > 0:
        price = Amount.from_string(maybe_price[0])
        comment = RE_PRICE.sub("", comment)
    else:
        price = None

    return comment, price


def extract_payee(narration: str):
    """Split full narration into payee and clean narration."""
    payee = RE_PAYEE.match(narration)
    if payee:
        return payee[0].strip("|").strip(), RE_PAYEE.sub("", narration, 1).strip()
    return None, narration.strip()


def extract_rest(comment: str):
    """Extract other_account, units, flag, payee, narration, tags, and links."""
    comment_tuple = comment.split()
    narration_tmp = " ".join(comment_tuple[4:-1])

    other_account = comment_tuple[0]
    units = Amount.from_string(" ".join(comment_tuple[1:3]))
    flag = comment_tuple[3]

    tags = {"NoteToTx"}
    for tag in RE_TAG.findall(narration_tmp):
        tags.add(tag[1])
    tags = frozenset(tags)
    narration_tmp = RE_TAG.sub("", narration_tmp).rstrip()

    links = set()
    for link in RE_LINK.findall(narration_tmp):
        links.add(link[1])
    links = frozenset(links)
    narration_tmp = RE_LINK.sub("", narration_tmp).rstrip()

    payee, narration = extract_payee(narration_tmp)

    return other_account, units, flag, tags, links, payee, narration


def to_oneliner(tx: data.Transaction, alignDotAt=90, alignAccountAt=50) -> data.Note:
    """
    Useful in custom importers to import transactions in oneliner format.

    Usage:
    ```
    tx_entry = data.Transaction(...)       # Given a transaction..
    note_entry = onelinerFromTx(tx_entry)  # Get a matching oneliner note.
    ```

    Assuming max account name length is 32, to acommodiate 6-digit numbers recommended alignDotAt is 90 (and alignAccountAt is 50).
    ```
    2020-01-02 note Assets:Cash                      "Expenses:Random                     123.45 EUR * ShopA | some stuff.. *"
    2020-01-02 note Assets:BankABC:Checking          "Expenses:Groceries                   43.21 EUR * ShopB | some groceries *"
    #                          |---------------------^               |-----------------------^
    #                                      |---------^                  |--------------------^
    #                                (alignAccountAt = 50)                       (alignDotAt = 90)

    2020-01-02 note Assets:Cash "Expenses:Random                                          123.45 EUR * ShopA | some stuff.. *"
    2020-01-02 note Assets:BankABC:Checking "Expenses:Groceries                            43.21 EUR * ShopB | some groceries *"
    #                                           |--------------------------------------------^
    #                                                          |-----------------------------^
    #                                (alignAccountAt = 0)                        (alignDotAt = 90)
    ```
    """

    tagString = " ".join(list(map(prefixHash, tx.tags)))
    tagLinks = " ".join(list(map(prefixCarrot, tx.links)))

    commentAccount = tx.postings[1].account
    commentRest = "{} * {} | {} {} {} *".format(tx.postings[1].units, tx.payee, tx.narration, tagString, tagLinks)

    preDotLen = len(str(tx.postings[1].units).split(".")[0])

    prefixLen = len("____-__-__ note " + tx.postings[0].account + ' "')
    middleLen = len(tx.postings[1].account + " ") + preDotLen
    pad = " " * max(1, (alignDotAt - prefixLen - middleLen - (max(0, alignAccountAt - prefixLen))))

    entry = data.Note(tx.meta, tx.date, tx.postings[0].account, commentAccount + pad + commentRest)

    return entry


def from_oneliner(note: data.Note, options_map):
    """
    Parse one note oneliner into a valid transactions. For example,
    1999-12-31 note Assets:Cash "Income:Test -16.18 EUR * Payee | Description goes here *"
    """
    comment = note.comment
    k = None

    comment, cost = extract_optional_cost(comment)
    if cost:
        k = k or mul(cost, D(-1))

    comment, price = extract_optional_price(comment)
    if price:
        k = k or mul(price, D(-1))

    other_account, units, flag, tags, links, payee, narration = extract_rest(comment)
    tags_merged = frozenset().union(tags, note.tags)
    links_merged = frozenset().union(links, note.links)
    k = k or Amount(D(-1), units.currency)

    # print(type(cost), cost, type(price), price, type(units), units, k, comment)
    p1 = data.Posting(
        account=other_account,
        units=units,
        cost=cost,
        price=price,
        flag=None,
        meta={"filename": note.meta["filename"], "lineno": note.meta["lineno"]},
    )
    p2 = data.Posting(
        account=note.account,
        units=mul(k, units.number),
        cost=cost,
        price=None,
        flag=None,
        meta={"filename": note.meta["filename"], "lineno": note.meta["lineno"]},
    )
    txn = data.Transaction(
        date=note.date,
        flag=flag,
        payee=payee,
        narration=narration,
        tags=tags_merged,
        links=links_merged,
        postings=[p1, p2],
        meta=note.meta,
    )

    # Get the AUTOMATIC_TOLERANCES meta that all transaction should have.
    # This is a simplified extraction from `infer_tolerances` function within beancount.
    tolerances = options_map["inferred_tolerance_default"].copy()
    expo = units.number.as_tuple().exponent
    tolerances[units.currency] = ONE.scaleb(expo) * options_map["inferred_tolerance_multiplier"]
    default = tolerances.pop("*", ZERO)
    meta = txn.meta.copy()
    meta[interpolate.AUTOMATIC_TOLERANCES] = defdict.ImmutableDictWithDefault(tolerances, default=default)

    return txn._replace(meta=meta)


# Good to remember that beancount passes these parameters to all plugins.
# pylint: disable=unused-argument
def oneliner(entries, options_map, config):
    """
    Parse note oneliners into valid transactions. For example,
    1999-12-31 note Assets:Cash "Income:Test -16.18 EUR * Payee | Description goes here *"
    """
    errors = []
    new_entries = []

    for entry in entries:
        # data.* are custom types, I think.
        # pylint: disable=isinstance-second-argument-not-valid-type
        if not (isinstance(entry, data.Note) and entry.comment[-1:] == "*"):
            new_entries.append(entry)
            continue

        try:
            new_entry = from_oneliner(entry, options_map)
            new_entries.append(new_entry)
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

    return new_entries, errors
