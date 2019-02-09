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
            output_folder = self._create_output_folder(self.enex_file)
            self._write_markdown(notes, output_folder)
        else:
            print("WARNING! ATTACHMENTS ARE NOT PROCESSED WITH STDOUT OUTPUT!")
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
            text_maker.emphasis_mark = '*'

            content_raw = note.xpath('content')[0].text

            # Preprosessors:
            content_pre = self._handle_lists(content_raw)
            content_pre = self._handle_tasks(content_pre)
            content_pre = self._handle_strongs_emphases(content_pre)
            content_pre = self._handle_tables(content_pre)

            if self.write_to_disk:
                content_pre = self._handle_attachments(content_pre)

            # Convert html > text
            content_text = text_maker.handle(content_pre)

            # Postprocessors:
            content_post1 = self._remove_extra_new_lines(content_text)

            keys['content'] = content_post1

            ''' Generate safe filename base for output.
            The final name will be generated when writing, because of duplicate check. '''
            keys['markdown_filename_base'] = self._make_safe_name(keys['title'])

            notes.append(keys)

        print(f"Processed {note_count} note(s).")
        return notes

    def _handle_attachments(self, text):
        """ Note content may have attachments, such as images.
        <div><en-media hash="..." type="application/pdf" style="cursor:pointer;" /></div>
        <div><en-media hash="..." type="image/png" /><br /></div>
        <div><en-media hash="..." type="image/jpeg" /></div>
        """
        return text

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

    def _handle_strongs_emphases(self, text):
        """ Make these work.
        <span style="font-weight: bold;">This text is bold.</span>
        <span style="font-style: italic;">This text is italic.</span>
        <span style="font-style: italic; font-weight: bold;">This text is bold and italic.</span>

        <div>
        <span style="font-style: italic; font-weight: bold;"><br /></span>
        </div>
        <div>This text is normal. <i><b>This text is bold and italic.</b></i> This text is normal again.</div>
        """
        parts = re.split(r'(<span.*?</span>)', text)

        new_parts = []
        for part in parts:
            match = re.match(r'<span style=(?P<formatting>.*?)>(?P<content>.*?)</span>', part)
            if match:
                if match.group('content') == '<br />':
                    part = '<br />'
                else:
                    if 'font-style: italic;' in match.group('formatting') and 'font-weight: bold;' in match.group('formatting'):
                        # part = f"<i><b>{match.group('content')}</b></i>"
                        part = f"<span>***{match.group('content')}***</span>"
                    elif 'font-weight: bold;' in match.group('formatting'):
                        # part = f"<b>{match.group('content')}</b>"
                        part = f"<span>**{match.group('content')}**</span>"
                    elif 'font-style: italic;' in match.group('formatting'):
                        # part = f"<i>{match.group('content')}</i>"
                        part = f"<span>*{match.group('content')}*</span>"
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

    def _make_safe_name(self, input_string=None, counter=0):
        better = input_string.replace(' ', '_')
        better = "".join([c for c in better if re.match(r'\w', c)])
        # For handling duplicates: If counter > 0, append to file/folder name.
        if counter > 0:
            better = f"{better}_{counter}"
        return better

    def _create_output_folder(self, input_name):
        ''' See that the folder does not exist. If it doesn't, create it.
            Name is created from a timestamp: 20190202_172208
        '''

        subfolder_name = input_name.split('/')[-1]
        subfolder_name = self._make_safe_name(subfolder_name.split('.')[0])

        folder_name = f"output/{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}/{subfolder_name}"
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
            # Check, that the file name does not exist already. If it does, generate a new one.
            filename = f"{output_folder}/{note['markdown_filename_base']}.md"
            counter = 0
            while os.path.exists(filename):
                counter += 1
                filename = f"{output_folder}/{self._make_safe_name(note['markdown_filename_base'], counter)}.md"

            with open(filename, 'w') as output_file:
                output_file.writelines("%s\n" % l for l in self._format_note(note))
