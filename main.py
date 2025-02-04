from epub_book_parser import EpubParser
from indexer import SpeechIndexer
from reparser import Reparser
from ebooklib import epub

if __name__ == "__main__":
    epub_file_path = "nebular_reduced.epub"

    parser = EpubParser(chunk_size=2000)
    indexer = SpeechIndexer("openai") # openai or deepseek (case-sensitive!!)
    book = epub.read_epub(epub_file_path)

    chunks = parser.parse(book)
    processed_chunks = []
    current_chapter = None
    chapter_content = ""

    for i, chunk in enumerate(chunks):
        if chunk.startswith("CHAPTER_START:"):
            if current_chapter:
                processed_chunks.append((current_chapter, chapter_content))
                chapter_content = ""
            current_chapter = chunk.split("CHAPTER_START:", 1)[1].strip()
        else:
            processed_chunk = indexer.process_text(chunk)
            chapter_content += processed_chunk

    if current_chapter:
        processed_chunks.append((current_chapter, chapter_content))

    # turns the processed input back into a book
    reparser = Reparser(book, processed_chunks)
    reparser.reparse()
    reparser.save("processed_book.epub")