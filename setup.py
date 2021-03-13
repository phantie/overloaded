"""Build with
   > py setup.py sdist"""

from setuptools import setup, find_packages
from os.path import join, dirname

__version__ = '1.2.2'

setup(
    author = 'phantie',
    name = 'overloaded',
    version = __version__,
    packages = find_packages(),
    long_description = open(join(dirname(__file__), 'README.rst')).read(),
    install_requires=['typeguard']
)