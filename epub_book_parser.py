import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import re
from item_chunk import Chunk

class EpubParser:
    def __init__(self, chunk_size=2000):
        self.chunk_size = chunk_size

    def parse(self, book):
        content_items = book.get_items_of_type(ebooklib.ITEM_DOCUMENT)
        chunks = []
        
        for item_index, item in enumerate(content_items):
            content = item.get_content().decode('utf-8')
            soup = BeautifulSoup(content, 'html.parser')
            body = soup.body

            if not body:
                print(f"Warning: No <body> tag found in item {item.file_name}")
                continue

            # Find all relevant tags (p, h1, h2, h3, div, etc.)
            elements = body.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'div'])

            chunk_index = 0
            current_chunk = ""
            for element in elements:
                element_str = str(element)
                if len(current_chunk) + len(element_str) > self.chunk_size:
                    if current_chunk:
                        chunks.append(Chunk(f"{item_index}.{chunk_index}", current_chunk.strip()))
                        chunk_index += 1
                    current_chunk = element_str
                else:
                    current_chunk += element_str + "\n"

            # Append the last chunk of the item
            if current_chunk:
                chunks.append(Chunk(f"{item_index}.{chunk_index}", current_chunk.strip()))

        return chunks
