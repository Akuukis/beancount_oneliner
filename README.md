# How to use

Two leg simple amount transactions are supported, because they are the bulk of entries. Support for price and cost may come, feel free to contribute.

```
1999-12-31 note Assets:Cash "Income:Test -16.18 EUR ! Description goes here *"
```

will be translated into

```
1999-12-31 ! "Description goes here"
	Income:Test		-16.18 EUR
	Assets:Cash
```

# Install

Copy to path used for python. For example, `$HOME/.local/lib/python3.5/site-packages/beanoneliner/beanoneliner.py` would do on Debian. If in doubt, look where `beancount` folder is and copy next to it.

# Syntax highlight

## Sublime

YAML-tmLanguage entry of [beancount syntax definition for Sublime Text](https://github.com/draug3n/sublime-beancount)

```yaml
- comment: note oneliner directive
  name: meta.directive.notetotext.beancount
  begin: ([0-9]{4})([\-|/])([0-9]{2})([\-|/])([0-9]{2})\s+(note)(?=(.*\*\"\s))
  beginCaptures:
    '1': {name: constant.numeric.date.year.beancount}
    '2': {name: punctuation.separator.beancount}
    '3': {name: constant.numeric.date.month.beancount}
    '4': {name: punctuation.separator.beancount}
    '5': {name: constant.numeric.date.day.beancount}
    '6': {name: support.function.directive.beancount}
  end: (?=(^\s*$|^\S))
  patterns:
  - include: '#meta'
  - include: '#account'
  - name: punctuation.separator.beancount
    match: (?<=\s)\"
  - include: '#cost'
  - include: '#amount'
  - begin: (\*|\!)
    beginCaptures:
      '0': {name: support.function.directive.beancount}
    end: (\*\")
    endCaptures:
      '0': {name: punctuation.separator.beancount}
    patterns:
    - name: constant.character.escape.beancount
      match: \\.
    - include: '#tag'
    - name: string.quoted.double.beancount
      match: ([^\"])
  - include: '#illegal'

```
