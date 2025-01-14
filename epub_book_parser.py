import os
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import re

def parse_epub(epub_file, chunk_size):
    book = epub.read_epub(epub_file)
    content_items = book.get_items_of_type(ebooklib.ITEM_DOCUMENT)
    chunks = []
    current_chunk = ""

    for item in content_items:
        content = item.get_content().decode('utf-8')
        soup = BeautifulSoup(content, 'html.parser')
        text = soup.get_text()
        paragraphs = re.findall(r'<p[^>]*>.*?</p>', content, re.DOTALL)

        for p in paragraphs:
            if len(current_chunk) + len(p) > chunk_size:
                chunks.append(current_chunk.strip())
                current_chunk = p
            else:
                current_chunk += p

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


epub_file_path = "/home/gelb/Documents/AudioBook NEBULAR 73 DE/Manuskript/nebular_073_de_ePub3.epub"

chunk_size = 2000  

chunks = parse_epub(epub_file_path, chunk_size)

if chunks:
    print("First chunk:")
    print(chunks[0])
    print("\nSecond chunk:")
    print(chunks[1])
else:
    print("No chunks were created.")

# print(f"Total number of chunks: {len(chunks)}")