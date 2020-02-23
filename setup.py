#!/usr/bin/env python3

from setuptools import setup

# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='beancount_oneliner',
    version='1.0.5',
    description='Plugin for Beancount to write oneliner transaction entries.',

    long_description=long_description,
    long_description_content_type='text/markdown',

    author='Kalvis \'Akuukis\' Kalnins',
    author_email='akuukis@kalvis.lv',
    license='GPLv3',
    package_data={'beancount_oneliner': ['README.md']},
    package_dir={'beancount_oneliner': 'beancount_oneliner'},
    packages=['beancount_oneliner'],
    requires=['beancount (>2.0)'],
    url='https://github.com/Akuukis/beancount_oneliner',
)
