# enex2md

Enex2md is a command-line utility to convert Evernote export files (`*.enex`) to Markdown.

At the moment, this is more of a prototype, than actual conversion tool.

**THIS IS VERY MUCH WORK IN PROGRESS.**

## Installation

`pip install -U enex2md`

## Usage

To use the CLI after installing, run the conversion with:
`enex2md [enex-file-to-process]`

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
