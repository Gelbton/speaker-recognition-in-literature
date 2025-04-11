import tkinter as tk
from ebooklib import epub
from epub_book_parser import EpubParser
from indexer import SpeechIndexer
from reparser import Reparser
from gui import SpeakerAliasUI

def main():
    epub_file_path = "nebular_reduced.epub"
    book = epub.read_epub(epub_file_path)
    parser = EpubParser(chunk_size=2000)
    chunks = parser.parse(book)

    indexer = SpeechIndexer("openai")  # alternative: "deepseek"
    processed_chunks = []
    for i, chunk in enumerate(chunks):
        processed_chunk = indexer.process_chunk(chunk)
        processed_chunks.append(processed_chunk)
        print(f"Processed Chunkgroup {processed_chunk.get_index()} Number {i+1}")

    root = tk.Tk()
    app = SpeakerAliasUI(root)
    root.mainloop()

    final_mapping = app.get_final_mapping()

    reparser = Reparser(book, processed_chunks, final_mapping=final_mapping)
    reparser.save("output.epub")

if __name__ == "__main__":
    main()