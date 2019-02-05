# enex2md

Enex2md is a command-line utility to convert Evernote export files (`*.enex`) to [GitHub Flavored Markdown](https://github.github.com/gfm/).

## Features

In addition to the content itself, the note metadata is included in the resulting Markdown.

Within the content, the following features are supported:

- [x] Lists
- [x] Tables created within Evernote are converted to [GFM Tables](https://github.github.com/gfm/#table).
- [x] Tasks are converted to [GFM Task list items](https://github.github.com/gfm/#task-list-item)
- [x] Subsequent empty lines are compressed to one.

The html in enex files is *somewhat interesting*, thus some *magic is used to massage the data to functioning feature-rich Markdown*. Since the Magic Book has not yet been fully written, there are a couple of **known issues**:

- Strong, emphasis and strong emphasis are lost in some cases.
- Attachments are not handled at the moment.
- Codeblocks are not handled correctly.
- Images are lost (technically they are attachments in enex).

**This is work in progress, but should already generate useful results.**

See [Changelog](https://github.com/janikarh/enex2md/blob/master/CHANGELOG.md) for more details.

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
