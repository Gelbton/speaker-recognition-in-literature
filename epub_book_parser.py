import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import re

import re
import ebooklib
from ebooklib import epub

class EpubParser:
    def __init__(self, chunk_size=2000):
        self.chunk_size = chunk_size


    def parse(self, book):
        
        content_items = book.get_items_of_type(ebooklib.ITEM_DOCUMENT)
        chunks = []
        current_chunk = ""
        current_chapter = None

        # build chapter mapping from TOC (table of contents) to avoid chunks overlapping chapters
        chapter_map = {}
        for entry in book.toc:
            # extract base filename from href (ignore anchor links) - test if this is robust enough in the future
            href_base = entry.href.split('#')[0] # href_base is the .xhtml file a table entry would link (without sections)
            chapter_map[href_base] = entry.title # chapter map is a dictionary mapping files to their respective chapters

        for item in content_items:
            item_name = item.get_name() 
            new_chapter = chapter_map.get(item_name) # store current chapter/file we are reading in

            # Chapter boundary detection
            if new_chapter and new_chapter != current_chapter:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = ""
                current_chapter = new_chapter
                current_chunk += f"\n___CHAPTER_START___: {current_chapter}\n" # choosing triple underscore to avoid collision

            content = item.get_content().decode('utf-8')
            paragraphs = re.findall(r'<p[^>]*>.*?</p>', content, re.DOTALL)

            for p in paragraphs:
                cleaned_p = re.sub(r'<.*?>', '', p)  # Remove HTML tags
                
                if len(current_chunk) + len(cleaned_p) > self.chunk_size:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = f"{current_chapter}\n" if current_chapter else ""
                    current_chunk += cleaned_p
                else:
                    current_chunk += cleaned_p + "\n"

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

