class TextProcessor:
    def __init__(self, parser, indexer):
        self.parser = parser
        self.indexer = indexer

    def process_epub(self, epub_file):
        chunks = self.parser.parse(epub_file)
        processed_chunks = []
        
        for i, chunk in enumerate(chunks):
            processed_chunk = self.indexer.process_text(chunk)
            processed_chunks.append(processed_chunk)
            
            # immediate print
            print(f"\nChunk {i+1}:")
            print("=" * 50)
            print(processed_chunk)
            print("=" * 50)
            
        return processed_chunks