from pypdf import PdfReader
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PDFLoader:
    """
    Loads a PDF file and extracts text.
    """

    def load(self, pdf_path: str) -> str:
        """
        Extract text from a PDF.

        Args:
            pdf_path: Path to PDF file.

        Returns:
            Extracted text.
        """

        if not os.path.exists(pdf_path):
            raise FileNotFoundError(
                f"PDF file '{pdf_path}' not found."
            )

        try:
            logger.info("Loading PDF...")

            reader = PdfReader(pdf_path)

            text = ""

            for page in reader.pages:
                page_text = page.extract_text()

                if page_text:
                    text += page_text + "\n"

            logger.info("PDF loaded successfully!")

            return text

        except Exception as e:
            raise RuntimeError(
                f"Failed to read PDF: {e}"
            )


if __name__ == "__main__":

    loader = PDFLoader()

    pdf_text = loader.load("sample.pdf")

    logger.info(f"Characters: {len(pdf_text)}")
    print()
    print(pdf_text[:500])