
[![PyPI - Version](https://img.shields.io/pypi/v/beancount_oneliner)](https://pypi.org/project/packages/beancount_oneliner/)
![PyPI - Downloads](https://img.shields.io/pypi/dm/beancount_oneliner)
![PyPI - Wheel](https://img.shields.io/pypi/wheel/beancount_oneliner)
![PyPI - License](https://img.shields.io/pypi/l/beancount_oneliner)


## How to use

Two leg simple amount transactions are supported, because they are the bulk of entries. Support for price and cost may come, feel free to contribute.

```bean
1999-12-31 note Assets:Cash "Income:Test -16.18 EUR ! Description goes here #myTag *"
```

will be translated into

```bean
1999-12-31 ! "Description goes here" #myTag
	Income:Test		-16.18 EUR
	Assets:Cash
```


## Install

```sh
pip3 install beancount_oneliner --user
```

Or copy to path used for python. For example, `$HOME/.local/lib/python3.4/site-packages/beancount_oneliner/oneliner.py` would do on Debian. If in doubt, look where `beancount` folder is and copy next to it.

Recommended VSCode themes:
- Ayu
- Monokai Pro
- Night Owl


## Syntax highlight

Supported by the following beancount extensions:
- [beancount syntax definition for Sublime Text](https://github.com/draug3n/sublime-beancount)
- [VSCode Beancount Extension](https://github.com/Lencerf/vscode-beancount)

On VSCode, you will need to select the syntax with plugin support (there are two, with and without). To ensure it's selected automatically, add this to VSCode settings:
```jsonc
    "files.associations": {
        "*.extract": "beancount-oneline",
        "*.bean": "beancount-oneline",
        "*.beancount": "beancount-oneline",
    }
```
