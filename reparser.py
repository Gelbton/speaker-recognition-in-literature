import re
import ebooklib
from ebooklib import epub

class Reparser:
    def __init__(self, book, chunks, final_mapping=None):
        self.book = book
        self.chunks = chunks
        self.final_mapping = final_mapping

    def update_speaker_mapping(self, text, mapping):
        def repl(match):
            tag = match.group(1)
            speaker = match.group(2)
            for group_name, aliases in mapping.items():
                colour = self.stringToColour(group_name) # simply casts the group name into an individual random colour
                if speaker in aliases:
                    return f'<{tag} style="background-color:{colour};" speaker="{group_name}">'
            return match.group(0)
        
        pattern = r'<(speech|em) speaker="([^"]+)">'
        updated_text = re.sub(pattern, repl, text)
        return updated_text

    def reparse(self):
        new_book = self.book

        chunk_dict = {}
        for chunk in self.chunks:
            item_index = int(chunk.get_index().split('.')[0])
            if item_index not in chunk_dict:
                chunk_dict[item_index] = []
            chunk_dict[item_index].append(chunk)

        print(f"Number of chunk groups: {len(chunk_dict)}")
        for index, chunks in chunk_dict.items():
            print(f"Chunk group index: {index}, number of chunks: {len(chunks)}")

        html_items = list(new_book.get_items_of_type(ebooklib.ITEM_DOCUMENT))
        print(f"Number of HTML items: {len(html_items)}")

        for i, item in enumerate(html_items):
            print(f"Processing item {i}: {item.file_name}")

            chunk_group = chunk_dict.get(i, None)

            if chunk_group:
                print(f"Found chunk group for index {i}")
                combined_content = ''.join(chunk.get_content() for chunk in chunk_group)
                if self.final_mapping:
                    combined_content = self.update_speaker_mapping(combined_content, self.final_mapping)
                print(f"New content preview: {combined_content[:100]}...")
                item.set_content(combined_content.encode('utf-8'))
            else:
                print(f"No chunk group found for index {i}")

        return new_book

    def save(self, output_filename):
        new_book = self.reparse()
        epub.write_epub(output_filename, new_book)

def stringToHighlighterColour(self, string):
    hash = 0
    for char in string:
        hash = ord(char) + ((hash << 5) - hash)
    colour = '#'
    for i in range(3):
        value = (hash >> (i * 8)) & 0xff
        # Skaliere den Wert in den Bereich 180–255 (sehr hell)
        value = int(180 + (value / 255) * (255 - 180))
        colour += format(value, '02x')
    return colour

