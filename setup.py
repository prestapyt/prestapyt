#!/usr/bin/env python

import sys, os
from setuptools import setup
from setuptools import find_packages

__author__ = 'Guewen Baconnier <guewen.baconnier@gmail.com>'
__version__ = '0.1.0'

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
	# Basic package information.
	name = 'prestapyt',
	version = __version__,
	packages = find_packages(),

	# Packaging options.
	include_package_data = True,

	# Package dependencies.
	install_requires = ['httplib2',],

	# Metadata for PyPI.
	author = 'Guewen Baconnier',
	author_email = 'guewen.baconnier@gmail.com',
	license = 'GNU AGPL-3',
	url = 'http://github.com/guewen/prestapyt/tree/master',
	keywords = 'prestashop api client rest',
	description = 'A library to access Prestashop data with Python.',
	long_description = read('README'),
	classifiers = [
		'Development Status :: 4 - Beta',
		'Intended Audience :: Developers',
		'License :: OSI Approved :: GNU Affero General Public License v3',
		'Topic :: Software Development :: Libraries :: Python Modules',
		'Topic :: Internet :: WWW/HTTP :: Site Management',
		'Topic :: Internet'
	]
)
