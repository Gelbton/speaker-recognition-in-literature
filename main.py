from epub_book_parser import EpubParser
from indexer import SpeechIndexer
from processor import TextProcessor


if __name__ == "__main__":
    parser = EpubParser(chunk_size=2000)
    indexer = SpeechIndexer()
    processor = TextProcessor(parser, indexer)

    epub_file_path = "nebular_073_de_ePub3.epub"
    processed_chunks = processor.process_epub(epub_file_path)