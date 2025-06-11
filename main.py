import tkinter as tk
from ebooklib import epub
from epub_book_parser import EpubParser
from indexer import SpeechIndexer
from reparser import Reparser
from gui import SpeakerAliasUI

def main():
    
    # Follow all comment instructions in this file to run the script. Note that you need to have the required libraries installed.
    
    # make sure you have added your OpenAI or DeepSeek API key to the environment variables
    # your API key should be stored in an environment variable named "OPENAI_API_KEY"
    
    epub_file_path = "path/to/your/book.epub"  # Replace with your EPUB file path
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
    reparser.save("output.epub") # here you can specify the output file name and a path relative to the current working directory
    
    # Run this script to start the processing
    # When the GUI opens, make sure to create a group for each speaker, even if they have no aliases.
    # done - now you should have a new EPUB file with the speakers highlighted in the text.
    
    # optional:
    # if you have a labeled version of your book, using this embedding style you may use the benchmark.py script to compare the results of your reparser with the ground truth.
    # further instructions are in the benchmark.py file.
if __name__ == "__main__":
    main()