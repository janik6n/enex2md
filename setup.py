# !/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

# Package meta-data.
NAME = 'enex2md'
DESCRIPTION = 'Convert enex to Markdown.'
VERSION = '0.0.3'
URL = 'https://github.com/janikarh/enex2md'
EMAIL = 'janikarh@gmail.com'
AUTHOR = 'Jani Karhunen'
REQUIRES_PYTHON = '>=3.6.0'

REQUIRED = ['click',
            'lxml>=4.3.0']

# Import the README and use it as the long-description.
with open("README.md", "r") as readme:
    long_description = readme.read()


setup(
    name=NAME,
    version=VERSION,
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
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Text Processing',
        'Topic :: Utilities',
    ],
)
