from itertools import groupby
from operator import attrgetter
from ebooklib import epub

class Reparser:
    def __init__(self, book, chunks):
        self.book = book
        self.chunks = chunks

    def reparse(self):
        # output epub
        new_book = epub.EpubBook()
        self.copy_metadata(new_book)
        # Group chunks by index
        grouped_chunks = groupby(sorted(self.chunks, key=attrgetter('index')), key=attrgetter('index'))

        # Create new items for the modified content
        new_items = []
        for index, group in grouped_chunks:
            print("\n")
            print("\n")
            print(index)
            print("\n")
            print("\n")
            # Combine all chunk contents for this index
            combined_content = ''.join(chunk.get_content() for chunk in group)
            print("Inhalt in Kapitel: " + "\n" + combined_content)
            item = epub.EpubHtml(file_name=f'body{index}.xhtml')
            item.content = combined_content
            new_book.add_item(item)
            new_items.append(item)

        # Add the items to the book's spine
        new_book.spine = ['nav'] + new_items

        # Add navigation files
        new_book.add_item(epub.EpubNcx())
        new_book.add_item(epub.EpubNav())

        return new_book

    
    # copies metadata into new book
    def copy_metadata(self, new_book):
        for namespace in self.book.metadata:
            for name, values in self.book.metadata[namespace].items():
                for value, others in values:
                    if namespace == 'DC':  # if block for Dublin Core metadata
                        if name == 'title':
                            print("title: \n " + value)
                            new_book.set_title(value)
                        elif name == 'language':
                            print("language: \n " + value)
                            new_book.set_language(value)
                        else:
                            new_book.add_metadata('DC', name, value, others)
                    else:  # handling of all other metadata formats/standards
                        print("\nelse case: " + namespace, name, value, others)
                        new_book.add_metadata(namespace, name, value, others)


    def save(self, output_filename):
        new_book = self.reparse()
        epub.write_epub(output_filename, new_book)
