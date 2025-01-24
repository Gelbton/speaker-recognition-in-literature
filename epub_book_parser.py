import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import re

class EpubParser:
    def __init__(self, chunk_size=2000):
        self.chunk_size = chunk_size

    def parse(self, epub_file):
        book = epub.read_epub(epub_file)
        content_items = book.get_items_of_type(ebooklib.ITEM_DOCUMENT)
        chunks = []
        current_chunk = ""

        for item in content_items:
            content = item.get_content().decode('utf-8')
            paragraphs = re.findall(r'<p[^>]*>.*?</p>', content, re.DOTALL)

            for p in paragraphs:
                print(p)
                if len(current_chunk) + len(p) > self.chunk_size:
                    chunks.append(current_chunk.strip())
                    current_chunk = p
                else:
                    current_chunk += p

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks