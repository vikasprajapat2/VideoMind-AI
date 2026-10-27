import html
import re
TRAGET_SECONDS = 30 
MAX_GAP_SECONDS = 3

SENTENCE_END = ".?!…।॥"

# ONLY FOR ENGLISH TRANSCRIPTION    
FILLER_WORDS = re._compiler(r"\b(?:u+m+|u+h+|e+r+m*|a+h+|h+m+|m{2,})\b[,.]?", re.IGNORECASE)
FILLER_PHRASES = re._compiler(r"\b(?:basically|you know,|i mean,)\s*", re.IGNORECASE)
LEADING_MARKERS = re.compile(r"^(?:(?:okay|ok|alright|well)\b[,\s]*)?(?:so\b[,\s]*)?", re.IGNORECASE)


# THIS TYPE  OF  words if its repit to stutter consider one

STUTTER_WORDS = {
    "i", "we", "you", "they", "he", "she", "it", "the", "a", "an", "to", "and", "so",
    "is", "in", "of", "that", "this", "but", "or", "for", "on", "at", "with", "be", "are",
}

def detect_language(text: str) -> str:
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return "unknown"
    n=len(letters)
    if sum('\u0900' <= c <='\u097f' for c in letters) / n > 0.3:
        return 'hi'
    if sum('\u0600' <= c <= '\u06ff' for c in letters) / n > 0.3:
        return 'ar'
    if sum("\u4e00" <= c <= "\u9fff" for c in letters) / n > 0.3:
        return "zh"
    if sum(c.isascii() for c in letters) / n > 0.8:
        return "en"
    return "unknown"
    