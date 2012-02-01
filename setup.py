#!/usr/bin/env python

import os
from setuptools import setup

__author__ = 'Guewen Baconnier <guewen.baconnier@gmail.com>'
__version__ = '0.1.1'

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

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
