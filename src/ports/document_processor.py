from abc import ABC, abstractmethod
from typing import BinaryIO

class DocumentProcessorPort(ABC):
    @abstractmethod
    def extract_text(self, file: BinaryIO, filename: str) -> str:
        """
        Extracts text from a given file-like object.
        Supports .txt and .pdf (via child implementations).
        """
        pass
