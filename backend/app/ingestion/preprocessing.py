"""
Text preprocessing utilities for document ingestion.
Handles normalization, cleaning, and boilerplate removal before chunking.
"""
import re
import unicodedata
from typing import List
from collections import Counter


def normalize_unicode(text: str) -> str:
    """Normalize unicode to NFKC form for consistency."""
    return unicodedata.normalize('NFKC', text)


def normalize_whitespace(text: str) -> str:
    """
    Normalize whitespace:
    - Replace tabs with spaces
    - Collapse multiple spaces into one
    - Remove trailing/leading whitespace from lines
    - Collapse multiple newlines (>2) into double newline
    """
    # Replace tabs with spaces
    text = text.replace('\t', ' ')
    
    # Collapse multiple spaces
    text = re.sub(r' +', ' ', text)
    
    # Strip whitespace from each line
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(lines)
    
    # Collapse excessive newlines (keep max 2)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()


def dehyphenate(text: str) -> str:
    """
    Remove line-break hyphens that split words across lines.
    Example: "informa-\ntion" -> "information"
    """
    # Match hyphen at end of line followed by lowercase letter
    # This pattern is conservative to avoid removing intentional hyphens
    text = re.sub(r'(\w)-\s*\n\s*(\w)', r'\1\2', text)
    return text


def remove_page_numbers(text: str) -> str:
    """
    Remove standalone page numbers (lines that are just numbers or 'Page N').
    """
    lines = text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        stripped = line.strip()
        # Skip lines that are just numbers
        if re.match(r'^[\d\-]+$', stripped):
            continue
        # Skip lines like "Page 5" or "- 5 -"
        if re.match(r'^[-\s]*(?:page\s*)?\d+[-\s]*$', stripped, re.IGNORECASE):
            continue
        cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)


def detect_repeated_headers_footers(pages_text: List[str], threshold: float = 0.7) -> List[str]:
    """Detect headers/footers that appear repeatedly across pages."""
    if len(pages_text) < 3:
        return []
    
    first_lines = []
    last_lines = []
    
    for page_text in pages_text:
        lines = [l.strip() for l in page_text.split('\n') if l.strip()]
        if lines:
            first_lines.extend(lines[:3])
            last_lines.extend(lines[-3:])
    
    all_candidates = first_lines + last_lines
    line_counts = Counter(all_candidates)
    
    min_occurrences = int(len(pages_text) * threshold)
    repeated_patterns = [
        line for line, count in line_counts.items()
        if count >= min_occurrences and len(line) > 5
    ]
    
    return repeated_patterns


def remove_repeated_patterns(text: str, patterns: List[str]) -> str:
    """
    Remove specific patterns (headers/footers) from text.
    """
    for pattern in patterns:
        # Escape special regex characters and create pattern
        escaped = re.escape(pattern)
        # Remove the pattern when it appears on its own line
        text = re.sub(rf'^\s*{escaped}\s*$', '', text, flags=re.MULTILINE)
    
    return text


def is_empty_or_garbage(text: str, min_length: int = 20) -> bool:
    """Check if text is empty or garbage."""
    cleaned = text.strip()
    
    if len(cleaned) < min_length:
        return True
    
    alphanumeric_count = sum(c.isalnum() for c in cleaned)
    if len(cleaned) > 0 and (alphanumeric_count / len(cleaned)) < 0.5:
        return True
    
    return False


def preprocess_text(raw: str, repeated_patterns: List[str] = None) -> str:
    """Main preprocessing: applies all cleaning steps."""
    if not raw:
        return ""
    
    text = normalize_unicode(raw)
    text = dehyphenate(text)
    text = normalize_whitespace(text)
    text = remove_page_numbers(text)
    
    if repeated_patterns:
        text = remove_repeated_patterns(text, repeated_patterns)
    
    text = normalize_whitespace(text)
    
    return text
