"""
PDF document parser using PyMuPDF (fitz).
Extracts text and images, with OCR fallback for scanned pages.
"""
import logging
from pathlib import Path
from typing import List, Optional

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

from .models import ParsedDocument, ParsedPage, PageImage
from .ocr import ocr_image, should_apply_ocr, is_tesseract_available

logger = logging.getLogger(__name__)


def parse_pdf(file_path: str, filename: str, ocr_fallback: bool = True) -> ParsedDocument:
    """Parse PDF document and extract text and images."""
    if not PYMUPDF_AVAILABLE:
        raise RuntimeError(
            "PyMuPDF is not available. Please install: pip install pymupdf"
        )
    
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"PDF file not found: {file_path}")
    
    # Check if OCR is available if requested
    ocr_available = ocr_fallback and is_tesseract_available()
    if ocr_fallback and not ocr_available:
        logger.warning("OCR fallback requested but Tesseract is not available")
    
    pages: List[ParsedPage] = []
    ocr_pages_used = 0
    
    try:
        # Open PDF
        doc = fitz.open(file_path)
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            page_number = page_num + 1  # 1-indexed
            
            # Extract text
            text = page.get_text()
            is_ocr = False
            
            # Check if page needs OCR (scanned or insufficient text)
            if ocr_available and should_apply_ocr(text):
                logger.info(f"Applying OCR to page {page_number} (insufficient text detected)")
                try:
                    # Render page to image
                    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x scaling for better OCR
                    img_bytes = pix.tobytes("png")
                    
                    # Apply OCR
                    ocr_text = ocr_image(img_bytes)
                    
                    if ocr_text and len(ocr_text.strip()) > len(text.strip()):
                        text = ocr_text
                        is_ocr = True
                        ocr_pages_used += 1
                    
                except Exception as e:
                    logger.error(f"OCR failed for page {page_number}: {e}")
            
            # Extract images from page
            images: List[PageImage] = []
            image_list = page.get_images()
            
            for img_index, img_info in enumerate(image_list):
                try:
                    xref = img_info[0]
                    base_image = doc.extract_image(xref)
                    
                    if base_image:
                        image_bytes = base_image["image"]
                        
                        # Optionally OCR the image
                        ocr_text = None
                        if ocr_available:
                            try:
                                ocr_text = ocr_image(image_bytes)
                            except Exception as e:
                                logger.debug(f"Image OCR failed for page {page_number}, image {img_index}: {e}")
                        
                        page_image = PageImage(
                            image_bytes=image_bytes,
                            page_number=page_number,
                            image_index=img_index,
                            width=base_image.get("width"),
                            height=base_image.get("height"),
                            format=base_image.get("ext", "").upper(),
                            ocr_text=ocr_text
                        )
                        images.append(page_image)
                
                except Exception as e:
                    logger.warning(f"Failed to extract image {img_index} from page {page_number}: {e}")
            
            # Create parsed page
            parsed_page = ParsedPage(
                page_number=page_number,
                text=text,
                images=images,
                is_ocr=is_ocr,
                metadata={
                    "width": page.rect.width,
                    "height": page.rect.height,
                    "rotation": page.rotation
                }
            )
            pages.append(parsed_page)
        
        # Extract document metadata
        metadata = {
            "title": doc.metadata.get("title", ""),
            "author": doc.metadata.get("author", ""),
            "subject": doc.metadata.get("subject", ""),
            "keywords": doc.metadata.get("keywords", ""),
            "creator": doc.metadata.get("creator", ""),
            "producer": doc.metadata.get("producer", ""),
            "creation_date": doc.metadata.get("creationDate", ""),
            "modification_date": doc.metadata.get("modDate", "")
        }
        
        doc.close()
        
        return ParsedDocument(
            filename=filename,
            source_format="pdf",
            pages=pages,
            total_pages=len(pages),
            ocr_pages_used=ocr_pages_used,
            metadata=metadata
        )
    
    except Exception as e:
        logger.error(f"Failed to parse PDF {filename}: {e}")
        raise
