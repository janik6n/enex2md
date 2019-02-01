"""Command Line Interface (CLI) for enex2md project."""

# import os
import sys

import click

from enex2md.convert import Converter
# from enex2md import __version__


@click.command()
@click.argument('input_file')
def app(input_file):
    """ Run the converter. Requires the input_file (data.enex) to be processed as the first argument. """
    print(f"Processing input file: {input_file}")
    # print(__version__)

    converter = Converter(input_file)
    converter.convert()

    sys.exit()


if __name__ == '__main__':
    app()
