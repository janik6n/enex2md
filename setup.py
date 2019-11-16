# !/usr/bin/env python
# -*- coding: utf-8 -*-

import io
import os
import re
from setuptools import setup

# Package meta-data.
NAME = 'enex2md'
DESCRIPTION = 'Convert enex to Markdown.'
URL = 'https://github.com/janikarh/enex2md'
EMAIL = 'janikarh@gmail.com'
AUTHOR = 'Jani Karhunen'
REQUIRES_PYTHON = '>=3.6.0'

REQUIRED = ['Click>=7.0',
            'lxml>=4.4.1',
            'python-dateutil>=2.7.0',
            'html2text>=2019.9.26',
            'beautifulsoup4>=4.8.1']

# The rest you shouldn't have to touch too much :)
# ------------------------------------------------

here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    with io.open(os.path.join(here, *parts), 'r') as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


# Import the README and use it as the long-description.
with open("README.md", "r") as readme:
    long_description = readme.read()


setup(
    name=NAME,
    version=find_version('enex2md', '__init__.py'),
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=['enex2md'],
    entry_points={
        'console_scripts': ['enex2md=enex2md.cli:app'],
    },
    install_requires=REQUIRED,
    include_package_data=True,
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Text Processing',
        'Topic :: Utilities',
    ],
)
