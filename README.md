# enex2md

Enex2md is a command-line utility to convert Evernote export files (`*.enex`) to Markdown.

In addition to the content itself, most of the metadata is included in the resulting Markdown.

Known issues:

- Tables are not handled / verified
- Lists are not handled / verified
- Attachments are not handled at all
- Tasks are not handled / verified
- Bold and italic text is not handled correctly.

**This is work in progress, but should already generate useful results.**

## Installation

Preferably in *a virtual environment*, run:

`pip install -U enex2md`

## Usage

To use the CLI after installing, run the conversion with:

`enex2md [enex-file-to-process]`

The output is written to `STDOUT` by default. If you want to write to disk instead, add a flag `--disk` to the command. This option will create a directory based on run time timestamp, and place individual files under that.

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
