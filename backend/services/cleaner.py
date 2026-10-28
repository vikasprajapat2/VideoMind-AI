import html
import re

TRAGET_SECONDS = 30 
MAX_SECONDS = 60  
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

#language detect
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

# each a every segment cleaning 
def _strip_noise(text: str) -> str:
    text = html.unescape(text)          # &amp; ko &, &quot; ko " mein convert karta hai.
    text = re.sub(r"\[[^\]]*\]", " ", text)  # IN S [] REMOVE A TEXT 
    text = re.sub(r"[♪♫]+", " ", text)   #music symboles remove
    text = text.replace(">>", " ")                  # speaker change marker
    text = re.sub(r"^\s*-\s+", "", text)     # starting lining 
    return text

def _remove_fillers(text: str) -> str:
    text = FILLER_WORDS.sub(" ", text)
    text = FILLER_PHRASES.sub(" ", text)
    return text

#normalize extra spaces aur punctuation
'''
Before	                After
"  Hello    world  "	    "Hello world"
"Hello , world !"	        "Hello, world!"
"Hello,,,"	                "Hello,"
",; Hello"	                "Hello"              
'''
def _normalize_ws(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip()                         
    text = re.sub(r"\s+([,.!?;:])", r"\1", text)
    text = re.sub(r"(,\s*)+,", ",", text)
    return re.sub(r"^[,;:\s]+", "", text)

# to remove overlap / duplicate transcript
def _norm(word: str) -> str:
    return re.sub(r"\W+", "" ,word.lower())

def _dedupe_overlaps(items: list) -> list:
    out, tail = [], []
    for start, end, text in items:
        words = text.split()
        norm = [_norm(w) for w in words]
        k = 0
        for size in range(min(len(tail). len(norm), 15),1, -1):
            if tail[-size:]== norm[:size]:
                k = size
                break
        words, norm = words[k:], norm[k:]
        if not words:
            if out:
                out[-1][1] = max(out[-1][1], end)
            continue
        out.append([start, end, " ".join(words)])
        tails = (tail + norm)[-15:]
    return out

#sentents chunks joints
def _build_chunks(items: list) -> list:
    if not items:
        return []
    punctuated = sum(t.rstrip().endswith(tuple(SENTENCE_END)) for _, _, t in items) / len(items) >= 0.1

    chunks, cur = [], None
    for start, end, text in items:
        if cur:
            length = cur[1] - cur[0]
            ends_sentence = (not punctuated) or cur[2].rstrip().endwith(tuple(SENTENCE_END))
            if (start - cur[1] > MAX_GAP_SECONDS or length >= MAX_SECONDS or (length >= TRAGET_SECONDS and ends_sentence)):
                chunks.append(cur)
                cur = None
        if cur is None:
            cur = [start, end, text]
        else:
            cur[1] = max(cur[1], end)
            cur[2] += " " + text
    chunks.append(cur)
    return chunks

def _collapse_stutters(text: str) -> str:
    def fix(m):
        return m.group(1) if m.group(1).lower() in STUTTER_WORDS else m.group(0)
    return re.sub(r"\b(\w+)(?:\s+\1\b)+", fix, text, flags=re.IGNORECASE)


def _strip_leading_markers(text: str) -> str:
    sentences = re.split(rf"(?<=[{re.escape(SENTENCE_END)}])\s+", text)
    cleaned = []
    for s in sentences:
        stripped = LEADING_MARKERS.sub("", s, count=1).strip()
        cleaned.append(stripped or s)
    return " ".join(cleaned)

def _format_text(text: str, english: bool) -> str:
    text = _collapse_stutters(text)
    if english:
        text = _strip_leading_markers(text)
        text = re.sub(r"\bi\b(?!\.\w)", "I", text)
    text = _normalize_ws(text)
    text = re.sub(rf"(^|[{re.escape(SENTENCE_END)}]\s+)([a-z])",
                  lambda m: m.group(1) + m.group(2).upper(), text)
    text = text.rstrip(",;: ")
    if text and not text.endswith(tuple(SENTENCE_END + "\"')")):
        has_devanagari = any("\u0900" <= c <= "\u097f" for c in text)
        text += "।" if has_devanagari else "."
    return text
