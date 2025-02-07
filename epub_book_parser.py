import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import re
from item_chunk import Chunk

class EpubParser:
    def __init__(self, chunk_size=2000):
        self.chunk_size = chunk_size

    def parse(self, book):
        """
        Parse the given book into chunks

        Parameters:
        book (ebooklib.epub.EpubBook): The EPUB book to parse.

        Returns:
        list: A list of Chunk objects.
        """
        content_items = book.get_items_of_type(ebooklib.ITEM_DOCUMENT) # list of .xhtml files
        chunks = []
        current_chunk = ""
        item_index = 0

        for item in content_items:
            content = item.get_content().decode('utf-8')
            paragraphs = re.findall(r'<p[^>]*>.*?</p>', content, re.DOTALL) # DOTALL to include linebreaks

            for p in paragraphs:
                if len(current_chunk) + len(p) > self.chunk_size:
                    if current_chunk:
                        chunks.append(Chunk(item_index, current_chunk.strip()))
                    current_chunk = p
                else:
                    current_chunk += p + "\n"

            item_index += 1

        # append the last chunk of the chapter as well
        if current_chunk:
            chunks.append(Chunk(item_index-1, current_chunk.strip()))

        return chunks
