import os
import ebooklib
from ebooklib import epub

def parse_epub(epub_file):
    book = epub.read_epub(epub_file)
    content_items = book.get_items_of_type(ebooklib.ITEM_DOCUMENT)
    
    with open('content.txt', 'w', encoding='utf-8') as f:
        for item in content_items:
            content = item.get_content().decode('utf-8')
            f.write(content)
            f.write('\n\n--- Next Section ---\n\n')

parse_epub('/home/gelb/Documents/sprechererkennung-ki/AudioBook NEBULAR 73 DE/Manuskript/nebular_073_de_ePub3.epub')
