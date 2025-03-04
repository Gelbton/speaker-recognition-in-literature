import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import re
from item_chunk import Chunk

class EpubParser:
    def __init__(self, chunk_size=2000):
        self.chunk_size = chunk_size

    def parse(self, book):
<<<<<<< HEAD
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
=======
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
>>>>>>> context-propagation

        return chunks
