try:
    from importlib.metadata import version, PackageNotFoundError
except:
    # for python < 3.8
    from importlib_metadata import version, PackageNotFoundError

__author__ = "Guewen Baconnier <guewen.baconnier@gmail.com>"

try:
    __version__ = version("prestapyt")
except PackageNotFoundError:
    # package is not installed
    __version__ = "0.0.0"
