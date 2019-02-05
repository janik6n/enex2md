import datetime
import json
import os
import re
import sys

from dateutil.parser import parse
import html2text
from lxml import etree


class Converter(object):

    date_format = '%h %d %Y %H:%M:%S'

    def __init__(self, enex_file, write_to_disk):
        self.enex_file = enex_file
        self.write_to_disk = write_to_disk

    def echo_info(self):
        return f"Enex-file: {self.enex_file}"

    def convert(self):
        if not os.path.exists(self.enex_file):
            print(f'ERROR: The given input file "{self.enex_file}" does not exist.')
            sys.exit(1)

        tree = etree.parse(self.enex_file)
        notes = self._parse_notes(tree)
        # self._export_notes(notes)

        if self.write_to_disk:
            output_folder = self._create_output_folder()
            self._write_markdown(notes, output_folder)
        else:
            self._print_markdown(notes)

    def _parse_notes(self, xml_tree):
        note_count = 0
        notes = []
        raw_notes = xml_tree.xpath('//note')
        for note in raw_notes:
            note_count += 1
            keys = {}
            keys['title'] = note.xpath('title')[0].text
            keys['created'] = f"{parse(note.xpath('created')[0].text).strftime(self.date_format)} GMT"
            if note.xpath('updated'):
                keys['updated'] = f"{parse(note.xpath('updated')[0].text).strftime(self.date_format)} GMT"
            keys['author'] = note.xpath('note-attributes/author')[0].text
            if note.xpath('note-attributes/source-url'):
                keys['source_url'] = note.xpath('note-attributes/source-url')[0].text
            keys['tags'] = [tag.text for tag in note.xpath('tag')]
            keys['tags_string'] = ", ".join(tag for tag in keys['tags'])

            ''' Content is HTML, and requires little bit of magic. '''

            text_maker = html2text.HTML2Text()
            text_maker.single_line_break = True
            text_maker.inline_links = True
            text_maker.use_automatic_links = False
            text_maker.body_width = 0

            content_raw = note.xpath('content')[0].text

            # Preprosessors:
            content_lists_handled = self._handle_lists(content_raw)
            content_tasks_handled = self._handle_tasks(content_lists_handled)
            content_tables_handled = self._handle_tables(content_tasks_handled)

            # Convert html > text
            content_text = text_maker.handle(content_tables_handled)

            # Postprocessors:
            content_post1 = self._remove_extra_new_lines(content_text)

            keys['content'] = content_post1

            ''' Generate safe filename for output. '''
            keys['markdown_filename'] = self._make_safe_filename(keys['title'])

            notes.append(keys)

        print(f"Processed {note_count} note(s).")
        return notes

    def _handle_tables(self, text):
        """ Split by tables. Within the blocks containing tables, remove divs. """

        parts = re.split(r'(<table.*?</table>)', text)

        new_parts = []
        for part in parts:
            if part.startswith('<table'):
                part = part.replace('<div>', '')
                part = part.replace('</div>', '')
            new_parts.append(part)

        text = ''.join(new_parts)

        return text

    def _handle_tasks(self, text):
        text = text.replace('<en-todo checked="true"/>', '<en-todo checked="true"/>[x] ')
        text = text.replace('<en-todo checked="false"/>', '<en-todo checked="false"/>[ ] ')
        return text

    def _handle_lists(self, text):
        text = re.sub(r'<ul>', '<br /><ul>', text)
        text = re.sub(r'<ol>', '<br /><ol>', text)
        return text

    def _remove_extra_new_lines(self, text):
        text = re.sub(r'\n+', '\n', text).strip()
        return text

    def _export_notes(self, notes):
        sys.stdout.write(json.dumps(notes, indent=4, sort_keys=True))

    def _make_safe_filename(self, input_string=None):
        better = input_string.replace(' ', '_')
        better = "".join([c for c in better if re.match(r'\w', c)])
        return f"{better}.md"

    def _create_output_folder(self):
        ''' See that the folder does not exist. If it doesn't, create it.
            Name is created from a timestamp: 20190202_172208
        '''
        folder_name = f"output/{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        return folder_name

    def _format_note(self, note):
        note_content = []
        note_content.append(f"# {note['title']}")
        note_content.append("")
        note_content.append("## Note metadata")
        note_content.append("")
        note_content.append(f"- Created by: {note['author']}")
        note_content.append(f"- Created at: {note['created']}")
        note_content.append(f"- Updated at: {note['updated']}")
        if 'source_url' in note:
            note_content.append(f"- Source URL: <{note['source_url']}>")
        note_content.append(f"- Tags: {note['tags_string']}")
        note_content.append("")
        note_content.append("## Note Content")
        note_content.append("")
        note_content.append(note['content'])

        return note_content

    def _print_markdown(self, notes):
        for note in notes:
            print("--- New Note ---")
            for line in self._format_note(note):
                print(line)
            print("--- End Note ---")

    def _write_markdown(self, notes, output_folder):
        for note in notes:
            with open(f"{output_folder}/{note['markdown_filename']}", 'w') as output_file:
                output_file.writelines("%s\n" % l for l in self._format_note(note))
