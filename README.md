# enex2md

[![version](https://img.shields.io/pypi/v/enex2md.svg?style=flat)](https://pypi.org/project/enex2md/)
[![platform](https://img.shields.io/pypi/pyversions/enex2md.svg?style=flat)](https://pypi.org/project/enex2md/)
[![wheel](https://img.shields.io/pypi/wheel/enex2md.svg?style=flat)](https://pypi.org/project/enex2md/)
[![downloads](https://img.shields.io/pypi/dm/enex2md.svg?style=flat)](https://pypi.org/project/enex2md/)
[![license](https://img.shields.io/github/license/janikarh/enex2md.svg?style=flat)](https://github.com/janikarh/enex2md/blob/master/LICENSE)

Enex2md is a command-line utility to convert Evernote export files (`*.enex`) to [GitHub Flavored Markdown](https://github.github.com/gfm/). *Python 3.6+ only!*

**NOTE: THIS PROJECT IS PRACTICALLY IN ARCHIVE MODE, AND WILL NOT BE UPDATED.**

## Features

In addition to the note content itself, the note metadata is included in the resulting Markdown. The enex-bundle may contain one or more notes.

Within the note content, the following features are supported:

- [x] Strong and emphasis text styles.
- [x] Ordered (i.e. numbered) and unordered lists
- [x] Tables created within Evernote are converted to [GFM Tables](https://github.github.com/gfm/#table)
- [x] Tasks are converted to [GFM Task list items](https://github.github.com/gfm/#task-list-item)
- [x] Images and other attachments
- [x] Code blocks
- [x] Subsequent empty lines are compressed to one.

The html in enex files is *somewhat interesting*, thus some *magic is used to massage the data to functioning feature-rich Markdown*. The Magic Book used here has not yet been fully written, so there might be some unfortunate side effects. Should you find one, [open an issue on GitHub](https://github.com/janikarh/enex2md/issues) with a well written description and **a test enex file** as an attachment.

See [Changelog](https://github.com/janikarh/enex2md/blob/master/CHANGELOG.md) for more details.

## Installation

**Installing to a virtual environment is strongly recommended.** To install, run:

`pip install -U enex2md`

## Usage

To use the CLI after installing, run the conversion with:

`enex2md [enex-file-to-process]`

The output is written to `STDOUT` by default. If you want to write to disk instead, add a flag `--disk` to the command. This option will create a directory based on run time timestamp, and place individual files under that.

*Please note, that on STDOUT output option attachments (including images) are not processed!*

## Development

Clone the [repository](https://github.com/janikarh/enex2md) to your local machine.

*I strongly recommend using a virtual environment for development.*

Install the requirements with:

`pip install -r requirements.txt`

From the root of the repository, you can run the app with:

`python -m enex2md.cli foo.enex`

After editing the content, try to install the package locally with:

`python setup.py install`

See that everything works. You can uninstall the dev package with `pip uninstall enex2md`.
