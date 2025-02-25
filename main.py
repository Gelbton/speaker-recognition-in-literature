from epub_book_parser import EpubParser
from indexer import SpeechIndexer
from reparser import Reparser 
from ebooklib import epub

if __name__ == "__main__":
    epub_file_path = "nebular_reduced.epub"
    book = epub.read_epub(epub_file_path)

    parser = EpubParser(chunk_size=2000)
    indexer = SpeechIndexer("openai") # openai or deepseek (case-sensitive!!)
    
    chunks = parser.parse(book)
    processed_chunks = []

    for i, chunk in enumerate(chunks):
        processed_chunk = indexer.process_chunk(chunk)
        processed_chunks.append(processed_chunk)

        print(f"\nChunkgroup {processed_chunk.get_index} Number {i+1}:")    

    reparser = Reparser(book, processed_chunks)
    reparser.save("output.epub")