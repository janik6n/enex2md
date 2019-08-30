import base64
import binascii
import datetime
import hashlib
import json
import os
import re
import sys

from bs4 import BeautifulSoup
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
            if note.xpath('note-attributes/author'):
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

            content_pre = note.xpath('content')[0].text

            # Preprosessors:
            if self.write_to_disk:
                content_pre = self._handle_attachments(content_pre)
            content_pre = self._handle_lists(content_pre)
            content_pre = self._handle_tasks(content_pre)
            content_pre = self._handle_strongs_emphases(content_pre)
            content_pre = self._handle_tables(content_pre)
            content_pre = self._handle_codeblocks(content_pre)

            # Convert html > text
            content_text = text_maker.handle(content_pre)

            # Postprocessors:
            content_post = self._post_processor_code_newlines(content_text)

            keys['content'] = content_post

            ''' Generate safe filename base for output.
            The final name will be generated when writing, because of duplicate check. '''
            keys['markdown_filename_base'] = self._make_safe_name(keys['title'])

            # Attachment data
            if self.write_to_disk:
                keys['attachments'] = []
                raw_resources = note.xpath('resource')
                for resource in raw_resources:
                    attachment = {}
                    attachment['filename'] = resource.xpath('resource-attributes/file-name')[0].text
                    # Base64 encoded data has new lines! Because why not!
                    clean_data = re.sub(r'\n', '', resource.xpath('data')[0].text).strip()
                    attachment['data'] = clean_data
                    attachment['mime_type'] = resource.xpath('mime')[0].text
                    keys['attachments'].append(attachment)

            notes.append(keys)

        print(f"Processed {note_count} note(s).")
        return notes

    def _handle_codeblocks(self, text):
        """ We would need to be able to recognise these (linebreaks added for brevity), and transform them to <pre> elements.
        <div style="box-sizing: border-box; padding: 8px; font-family: Monaco, Menlo, Consolas, &quot;Courier New&quot;, monospace; font-size: 12px; color: rgb(51, 51, 51); border-top-left-radius: 4px; border-top-right-radius: 4px; border-bottom-right-radius: 4px; border-bottom-left-radius: 4px; background-color: rgb(251, 250, 248); border: 1px solid rgba(0, 0, 0, 0.14902);-en-codeblock:true;">
        <div>import this</div>
        <div><br /></div>
        <div>my_data = this.create_object()</div>
        <div><br /></div>
        <div># One line comment.</div>
        <div><br /></div>
        <div>“”” A block comment</div>
        <div>    containing two lines.</div>
        <div>“”"</div>
        <div><br /></div>
        <div>print(my data)</div>
        </div>
        """
        soup = BeautifulSoup(text, 'html.parser')

        for block in soup.find_all(style=re.compile(r'.*-en-codeblock:true.*')):
            # Get the data, and set it in pre-element line by line.
            code = 'code-begin-code-begin-code-begin\n'
            for nugget in block.select('div'):
                code += f"{nugget.text}\n"
            code += 'code-end-code-end-code-end'

            # Fix the duoblequotes
            code = code.replace('“', '"')
            code = code.replace('”', '"')

            new_block = soup.new_tag('pre')
            new_block.string = code
            block.replace_with(new_block)

        return str(soup)

    def _handle_attachments(self, text):
        """ Note content may have attachments, such as images.
        <div><en-media hash="..." type="application/pdf" style="cursor:pointer;" /></div>
        <div><en-media hash="..." type="image/png" /><br /></div>
        <div><en-media hash="..." type="image/jpeg" /></div>
        """
        parts = re.split(r'(<en-media.*?/>)', text)
        new_parts = []
        for part in parts:
            if part.startswith('<en-media'):
                match = re.match(r'<en-media hash="(?P<md5_hash>.*?)".*? />', part)
                if match:
                    part = f"<div>ATCHMT:{match.group('md5_hash')}</div>"
            new_parts.append(part)
        text = ''.join(new_parts)
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
        text = text.replace('<en-todo checked="true" />', '<en-todo checked="true"/>[x] ')
        text = text.replace('<en-todo checked="false" />', '<en-todo checked="false"/>[ ] ')
        return text

    def _handle_lists(self, text):
        text = re.sub(r'<ul>', '<br /><ul>', text)
        text = re.sub(r'<ol>', '<br /><ol>', text)
        return text

    def _post_processor_code_newlines(self, text):
        new_lines = []
        for line in text.split('\n'):
            # The html2text conversion generates whitespace from enex. Let's remove the redundant.
            line = line.rstrip()

            if line == '**' or line == ' **':
                line = ''

            if line.startswith('    '):
                line = line[4:]

            if line == 'code-begin-code-begin-code-begin' or line == 'code-end-code-end-code-end':
                new_lines.append('```')
            else:
                new_lines.append(line)

        text = '\n'.join(new_lines)

        # Merge multiple empty lines to one.
        text = re.sub(r'\n{3,}', '\n\n', text).strip()

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
        if 'author' in note:
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
            filename_base = note['markdown_filename_base']
            filename = f"{output_folder}/{filename_base}.md"
            counter = 0
            while os.path.exists(filename):
                counter += 1
                filename_base = self._make_safe_name(note['markdown_filename_base'], counter)
                filename = f"{output_folder}/{filename_base}.md"

            """ Write attachments to disk, and fix references to note content.
            keys['attachments'][attachment_filename]['filename'] = attachment_filename
            keys['attachments'][attachment_filename]['data'] = resource.xpath('data')[0].text
            keys['attachments'][attachment_filename]['mime_type'] = resource.xpath('mime')[0].text
            """
            if 'attachments' in note and note['attachments']:
                attachment_folder_name = f"{output_folder}/{filename_base}_attachments"
                if not os.path.exists(attachment_folder_name):
                    os.makedirs(attachment_folder_name)

                for attachment in note['attachments']:
                    try:
                        decoded_attachment = base64.b64decode(attachment['data'])
                        with open(f"{attachment_folder_name}/{attachment['filename']}", 'wb') as attachment_file:
                            attachment_file.write(decoded_attachment)

                        # Create MD5 hash
                        md5 = hashlib.md5()
                        md5.update(decoded_attachment)
                        md5_hash = binascii.hexlify(md5.digest()).decode()

                        # Fix attachment reference to note content
                        note = self._fix_attachment_reference(
                            note,
                            md5_hash,
                            attachment['mime_type'],
                            f"{filename_base}_attachments",
                            attachment['filename']
                        )

                    except Exception as e:
                        print(f"Error processing attachment on note {filename_base}, attachment: {attachment['filename']}")
                        print(str(e))

            """ Write the actual markdown note to disk. """
            with open(filename, 'w') as output_file:
                output_file.writelines("%s\n" % l for l in self._format_note(note))

    def _fix_attachment_reference(self, note, md5_hash, mime_type, dir, name):
        content = note['content']
        if mime_type.startswith('image/'):
            content = content.replace(f"ATCHMT:{md5_hash}", f"\n![{name}]({dir}/{name})")
        else:
            # For other than image attachments, we write the same ! in the beginning.
            content = content.replace(f"ATCHMT:{md5_hash}", f"\n![{name}]({dir}/{name})")
        note['content'] = content
        return note
