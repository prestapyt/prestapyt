#! /bin/sh
python3 setup.py sdist upload
python3 setup.py bdist_egg upload
python3 setup.py bdist_wheel upload
