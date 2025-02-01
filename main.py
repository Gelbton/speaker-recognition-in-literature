from epub_book_parser import EpubParser
from indexer import SpeechIndexer

if __name__ == "__main__":
    epub_file_path = "nebular_073_de_ePub3.epub"

    parser = EpubParser(chunk_size=2000)
    indexer = SpeechIndexer("openai") # openai or deepseek (case-sensitive!!)

    chunks = parser.parse(epub_file_path)
    processed_chunks = []

    for i, chunk in enumerate(chunks):
        processed_chunk = indexer.process_text(chunk)
        processed_chunks.append(processed_chunk)

        print(f"\nChunk {i+1}:")
        print("=" * 50)
        print(processed_chunk)
        print("=" * 50)