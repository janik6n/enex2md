import json
import os
import sys

from lxml import etree


class Converter(object):

    def __init__(self, enex_file):
        self.enex_file = enex_file

    def echo_info(self):
        return f"Enex-file: {self.enex_file}"

    def convert(self):
        if not os.path.exists(self.enex_file):
            print(f'ERROR: The given input file "{self.enex_file}" does not exist.')
            sys.exit(1)

        tree = etree.parse(self.enex_file)
        notes = self._parse_notes(tree)
        # self._export_notes(notes)
        self._print_markdown(notes)

    def _parse_notes(self, xml_tree):
        notes = []
        raw_notes = xml_tree.xpath('//note')
        for note in raw_notes:
            keys = {}
            keys['title'] = note.xpath('title')[0].text
            keys['created'] = note.xpath('created')[0].text

            notes.append(keys)

        return notes

    def _export_notes(self, notes):
        sys.stdout.write(json.dumps(notes, indent=4, sort_keys=True))

    def _print_markdown(self, notes):
        for note in notes:
            print("--- New Note ---")
            print(f"# {note['title']}")
            print("Note metadata:")
            print(f"Created at: {note['created']}")
            print("--- End Note ---")
