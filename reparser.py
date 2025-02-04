import uuid
from ebooklib import epub

class Reparser:
    def __init__(self, book, content):
        self.book = book
        self.content = content

    def reparse(self):

        # output epub
        new_book = epub.EpubBook()

        # set identifier for the new book (no getter method exists for some reason)
        try:
            identifier = self.book.get_metadata('DC', 'identifier')[0][0]
            new_book.set_identifier(identifier)
        except (IndexError, AttributeError):
            # Generate a new identifier if one isn't found
            new_identifier = str(uuid.uuid4())
            new_book.set_identifier(new_identifier)

        # copy metadata from the original book
        # also no getter for this so time for quintuple inlined code
        for namespace in self.book.metadata:
            for name, values in self.book.metadata[namespace].items():
                for value, others in values:
                    if namespace == 'DC':
                        if name == 'title':
                            new_book.set_title(value)
                        elif name == 'language':
                            new_book.set_language(value)
                        else:
                            new_book.add_metadata('DC', name, value, others)
                    else:
                        new_book.add_metadata(namespace, name, value, others)


        # Create new items for the modified content
        new_items = []
        for i, (chapter_title, content) in enumerate(self.content):
            item = epub.EpubHtml(title=chapter_title, file_name=f'chapter{i+1}.xhtml', lang='en')
            item.content = content
            new_book.add_item(item)
            new_items.append(item)

        # Add the items to the books spine
        new_book.spine = ['nav'] + new_items

        # Add navigation files
        new_book.add_item(epub.EpubNcx())
        new_book.add_item(epub.EpubNav())

        return new_book

    def save(self, output_filename):
        new_book = self.reparse()
        epub.write_epub(output_filename, new_book)

