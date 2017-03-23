#!/usr/bin/env python

from distutils.core import setup

setup(
      name='beancount-oneliner',
      version='1.0.0',
      description='Oneliner entry plugin for Beancount',
      url='https://github.com/Akuukis/beancount_interpolate',
      author='Kalvis \'Akuukis\' Kalnins',
      author_email='akuukis@kalvis.lv',
      license='GPLv3',
      packages=['beancount-oneliner'],
      package_dir={'beancount-oneliner': 'src'},
      package_data={'beancount-oneliner': ['README.md']},
      requires=['beancount (>2.0)'],
     )
