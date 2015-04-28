#!/usr/bin/env python

"""
    Prestapyt

   :copyright: (c) 2011-2013 Guewen Baconnier
   :copyright: (c) 2011 Camptocamp SA
   :license: AGPLv3, see LICENSE for more details

"""

import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

with open('prestapyt/version.py') as f:
    # execute the file so __version__ is in the current scope
    exec(f.read())

setup(
    # Basic package information.
    name = 'prestapyt',
    version = __version__,

    # Packaging options.
    include_package_data = True,

    # Package dependencies.
    install_requires = ['httplib2',],

    # Metadata for PyPI.
    author = 'Guewen Baconnier',
    author_email = 'guewen.baconnier@gmail.com',
    license = 'GNU AGPL-3',
    url = 'http://github.com/guewen/prestapyt',
    packages=['prestapyt'],
    keywords = 'prestashop api client rest',
    description = 'A library to access Prestashop Web Service from Python.',
    long_description = read('README.md'),
    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Internet :: WWW/HTTP :: Site Management',
        'Topic :: Internet'
        ]
)
