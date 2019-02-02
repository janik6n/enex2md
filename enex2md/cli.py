"""Command Line Interface (CLI) for enex2md project."""

# import os
import sys

import click

from enex2md.convert import Converter
# from enex2md import __version__


@click.command()
@click.option('--disk', is_flag=True, help='output to disk instead of stdout (default)')
@click.argument('input_file')
def app(disk, input_file):
    """ Run the converter. Requires the input_file (data.enex) to be processed as the first argument. """
    if disk:
        output_option = 'DISK'
    else:
        output_option = 'STDOUT'
    print(f"Processing input file: {input_file}, writing output to {output_option}.")
    # print(__version__)

    converter = Converter(input_file, disk)
    converter.convert()

    sys.exit()


if __name__ == '__main__':
    app()
