#! /bin/sh
python2.7 setup.py sdist upload
python2.7 setup.py bdist_egg upload
python2.7 setup.py bdist_wheel upload
python3 setup.py sdist upload
python3 setup.py bdist_egg upload
python3 setup.py bdist_wheel upload
