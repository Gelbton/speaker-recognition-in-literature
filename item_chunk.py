

class Chunk:
    def __init__(self, index: str, content: str):
        self.index = index
        self.content = content

    def get_index(self) -> str:
        return self.index

    def get_content(self) -> str:
        return self.content

    def set_content(self, new_content: str):
        self.content = new_content

    def __str__(self):
        return f"Chunk(index={self.index}, content='{self.content}')"

    def __repr__(self):
        return self.__str__()