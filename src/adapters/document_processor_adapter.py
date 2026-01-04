import io
from typing import BinaryIO
from pypdf import PdfReader
from src.ports.document_processor import DocumentProcessorPort
import structlog

logger = structlog.get_logger()

class LocalDocumentProcessor(DocumentProcessorPort):
    def extract_text(self, file: BinaryIO, filename: str) -> str:
        logger.info("extracting_text", filename=filename)
        
        if filename.lower().endswith(".pdf"):
            return self._extract_from_pdf(file)
        elif filename.lower().endswith(".txt"):
            return file.read().decode("utf-8")
        else:
            raise ValueError(f"Unsupported file type: {filename}")

    def _extract_from_pdf(self, file: BinaryIO) -> str:
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text
