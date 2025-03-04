from itertools import groupby
from operator import attrgetter
import ebooklib
from ebooklib import epub

class Reparser:
    def __init__(self, book, chunks):
        self.book = book
        self.chunks = chunks

    def reparse(self):
        new_book = self.book

        # Group chunks by item index
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

            # Find the corresponding chunk group
            chunk_group = chunk_dict.get(i, None)

            if chunk_group:
                print(f"Found chunk group for index {i}")
                combined_content = ''.join(chunk.get_content() for chunk in chunk_group)
                print(f"New content preview: {combined_content[:100]}...")
                item.set_content(combined_content.encode('utf-8'))
            else:
                print(f"No chunk group found for index {i}")

        return new_book


    def save(self, output_filename):
        new_book = self.reparse()
        epub.write_epub(output_filename, new_book)
