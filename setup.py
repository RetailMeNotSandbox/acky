from __future__ import print_function
from setuptools import setup, find_packages
from acky import __version__
import sys

if sys.version_info <= (2, 7):
    error = "ERROR: acky requires Python 2.7 or later"
    print(error, file=sys.stderr)
    sys.exit(1)

with open('README.rst') as f:
    long_description = f.read()

setup(
    name="acky",
    version=__version__,
    description="A consistent API to AWS",
    long_description=long_description,
    author="Matthew Wedgwood",
    author_email="mw@rmn.com",
    url="http://github.com/RetailMeNot/acky",
    install_requires=[
        "botocore >= 0.45.0",
    ],
    packages=find_packages(),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Internet",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Topic :: Internet",
    ],
    license="MIT",
)
