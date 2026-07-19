"""OCR utilities using Tesseract."""
import io
import logging
from pathlib import Path
from typing import Union, TYPE_CHECKING

if TYPE_CHECKING:
    from PIL import Image

try:
    import pytesseract
    from PIL import Image
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    Image = None  # type: ignore

logger = logging.getLogger(__name__)


def is_tesseract_available() -> bool:
    """Check if Tesseract OCR is available."""
    if not TESSERACT_AVAILABLE:
        return False
    
    try:
        pytesseract.get_tesseract_version()
        return True
    except Exception as e:
        logger.warning(f"Tesseract not available: {e}")
        return False


def ocr_image(image_input: Union[bytes, str, Path, "Image.Image"], lang: str = 'eng') -> str:
    """Extract text from image using Tesseract OCR."""
    if not TESSERACT_AVAILABLE:
        raise RuntimeError("Tesseract OCR not available. Install: pip install pytesseract pillow")
    
    if not is_tesseract_available():
        raise RuntimeError("Tesseract binary not installed. See: https://github.com/tesseract-ocr/tesseract")
    
    try:
        if isinstance(image_input, bytes):
            from PIL import Image as PILImage
            image = PILImage.open(io.BytesIO(image_input))
        elif isinstance(image_input, (str, Path)):
            from PIL import Image as PILImage
            image = PILImage.open(image_input)
        elif Image and isinstance(image_input, Image.Image):
            image = image_input
        else:
            raise ValueError(f"Unsupported image input type: {type(image_input)}")
        
        text = pytesseract.image_to_string(image, lang=lang)
        return text.strip()
    
    except Exception as e:
        logger.error(f"OCR failed: {e}")
        return ""


def should_apply_ocr(text: str, min_text_threshold: int = 20) -> bool:
    """Check if OCR should be applied based on text length."""
    return len(text.strip()) < min_text_threshold


def estimate_text_confidence(text: str) -> float:
    """Estimate text quality (0.0 to 1.0)."""
    if not text or len(text.strip()) < 10:
        return 0.0
    
    total_chars = len(text)
    alphanumeric = sum(c.isalnum() or c.isspace() for c in text)
    
    if total_chars == 0:
        return 0.0
    
    char_score = alphanumeric / total_chars
    
    common_words = {'the', 'and', 'is', 'in', 'to', 'of', 'a', 'for', 'on', 'with'}
    words = text.lower().split()
    common_word_count = sum(1 for word in words if word in common_words)
    word_score = min(common_word_count / 5, 1.0) if words else 0.0
    
    confidence = (char_score * 0.7) + (word_score * 0.3)
    return min(confidence, 1.0)
