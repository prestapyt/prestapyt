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


setup(
    # Basic package information.
    name = 'prestapyt',
    use_scm_version=True,

    # Packaging options.
    include_package_data = True,

    # Package dependencies.
    install_requires = ['requests', 'future', 'importlib-metadata; python_version < "3.8"'],
    setup_requires=[
        'setuptools_scm',
    ],

    # Metadata for PyPI.

    author = 'Guewen Baconnier',
    author_email = 'guewen.baconnier@gmail.com',
    license = 'GNU AGPL-3',
    url = 'http://github.com/prestapyt/prestapyt',
    packages=['prestapyt'],
    keywords = 'prestashop api client rest',
    description = 'A library to access Prestashop Web Service from Python.',
    long_description_content_type='text/markdown',
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
