"""
Module 2: NLP Judgment Summarizer
Summarizes legal judgment text using transformer models with extractive fallback.
Extracts key legal information (parties, dates, statutes, case numbers).
"""

import re
import os
from collections import Counter

# Try importing transformers for abstractive summarization
try:
    from transformers import pipeline
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False

# Try importing NLTK for extractive summarization
try:
    import nltk
    from nltk.tokenize import sent_tokenize, word_tokenize
    from nltk.corpus import stopwords
    HAS_NLTK = True
    # Download required NLTK data silently
    for resource in ['punkt', 'punkt_tab', 'stopwords']:
        try:
            nltk.data.find(f'tokenizers/{resource}' if 'punkt' in resource else f'corpora/{resource}')
        except LookupError:
            try:
                nltk.download(resource, quiet=True)
            except Exception:
                pass
except ImportError:
    HAS_NLTK = False


# ── Abstractive Summarization (Transformers) ───────────────

_summarizer = None

def _get_summarizer():
    """Lazy-load the summarization pipeline."""
    global _summarizer
    if _summarizer is None and HAS_TRANSFORMERS:
        try:
            _summarizer = pipeline(
                "summarization",
                model="facebook/bart-large-cnn",
                device=-1  # CPU
            )
        except Exception:
            _summarizer = None
    return _summarizer


def abstractive_summarize(text, max_length=300, min_length=80):
    """Summarize text using BART model."""
    summarizer = _get_summarizer()
    if summarizer is None:
        return None

    # BART has a 1024 token limit, truncate if needed
    words = text.split()
    if len(words) > 900:
        text = ' '.join(words[:900])

    try:
        result = summarizer(
            text,
            max_length=max_length,
            min_length=min_length,
            do_sample=False,
            truncation=True
        )
        return result[0]['summary_text']
    except Exception:
        return None


# ── Extractive Summarization (NLTK / Pure Python) ─────────

def extractive_summarize(text, num_sentences=5):
    """
    Extractive summarization using sentence scoring.
    Works without any ML models.
    """
    # Sentence splitting
    if HAS_NLTK:
        try:
            sentences = sent_tokenize(text)
        except Exception:
            sentences = _simple_sent_tokenize(text)
    else:
        sentences = _simple_sent_tokenize(text)

    if len(sentences) <= num_sentences:
        return text

    # Word frequency scoring
    if HAS_NLTK:
        try:
            stop_words = set(stopwords.words('english'))
        except Exception:
            stop_words = _get_basic_stopwords()
        try:
            words = word_tokenize(text.lower())
        except Exception:
            words = text.lower().split()
    else:
        stop_words = _get_basic_stopwords()
        words = text.lower().split()

    # Clean words and count frequencies
    clean_words = [w for w in words if w.isalnum() and w not in stop_words and len(w) > 2]
    word_freq = Counter(clean_words)

    # Normalize frequencies
    if word_freq:
        max_freq = max(word_freq.values())
        word_freq = {w: f / max_freq for w, f in word_freq.items()}

    # Score sentences
    sentence_scores = {}
    for i, sent in enumerate(sentences):
        sent_words = sent.lower().split()
        score = sum(word_freq.get(w, 0) for w in sent_words if w.isalnum())

        # Boost score for sentences with legal keywords
        legal_keywords = [
            'court', 'judgment', 'order', 'held', 'petition', 'appeal',
            'section', 'act', 'article', 'constitution', 'respondent',
            'petitioner', 'accused', 'conviction', 'acquittal', 'verdict',
            'dismissed', 'allowed', 'disposed', 'plea', 'bail'
        ]
        for kw in legal_keywords:
            if kw in sent.lower():
                score += 0.5

        # Boost first and last sentences slightly
        if i == 0 or i == len(sentences) - 1:
            score += 0.3

        sentence_scores[i] = score

    # Select top sentences (maintain original order)
    top_indices = sorted(
        sorted(sentence_scores, key=sentence_scores.get, reverse=True)[:num_sentences]
    )

    summary = ' '.join(sentences[i] for i in top_indices)
    return summary


def _simple_sent_tokenize(text):
    """Basic sentence tokenizer without NLTK."""
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]


def _get_basic_stopwords():
    """Basic English stopwords without NLTK."""
    return {
        'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
        'should', 'may', 'might', 'shall', 'can', 'to', 'of', 'in', 'for',
        'on', 'with', 'at', 'by', 'from', 'as', 'into', 'through', 'during',
        'before', 'after', 'above', 'below', 'between', 'out', 'off', 'over',
        'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when',
        'where', 'why', 'how', 'all', 'each', 'every', 'both', 'few', 'more',
        'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own',
        'same', 'so', 'than', 'too', 'very', 'just', 'because', 'but', 'and',
        'or', 'if', 'while', 'about', 'this', 'that', 'these', 'those', 'it',
        'its', 'he', 'she', 'they', 'them', 'his', 'her', 'their', 'our',
        'my', 'your', 'we', 'us', 'me', 'him', 'which', 'who', 'whom'
    }


# ── Key Information Extraction ─────────────────────────────

def extract_key_points(text):
    """
    Extract structured key information from legal text.

    Returns dict with: case_numbers, dates, parties, statutes,
                       judges, court_names, legal_terms
    """
    key_points = {
        "case_numbers": [],
        "dates": [],
        "parties": [],
        "statutes": [],
        "judges": [],
        "court_names": [],
        "legal_terms": []
    }

    if not text:
        return key_points

    # Case numbers (various Indian formats)
    case_patterns = [
        r'(?:Case\s*No\.?\s*|W\.?P\.?\s*(?:\(C\)\s*)?No\.?\s*|SLP\s*(?:\(C\)\s*)?No\.?\s*|'
        r'Crl\.?\s*A\.?\s*No\.?\s*|C\.?A\.?\s*No\.?\s*|Civil\s*Appeal\s*No\.?\s*)'
        r'[\d/\-]+(?:\s*of\s*\d{4})?',
        r'\b\d+/\d{4}\b',
        r'\bSCI/\d{4}/\d+\b',
    ]
    for pattern in case_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        key_points["case_numbers"].extend(matches)

    # Dates (various formats)
    date_patterns = [
        r'\b\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4}\b',
        r'\b\d{1,2}\s+(?:January|February|March|April|May|June|July|August|'
        r'September|October|November|December)\s+\d{4}\b',
        r'\b(?:January|February|March|April|May|June|July|August|'
        r'September|October|November|December)\s+\d{1,2},?\s+\d{4}\b',
        r'\b\d{4}-\d{2}-\d{2}\b',
    ]
    for pattern in date_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        key_points["dates"].extend(matches)

    # Parties (petitioner vs respondent pattern)
    party_pattern = r'([A-Z][A-Za-z\s\.]+?)\s+(?:vs?\.?|versus)\s+([A-Z][A-Za-z\s\.]+?)(?:\.|,|\n|$)'
    party_matches = re.findall(party_pattern, text)
    for petitioner, respondent in party_matches:
        key_points["parties"].append({
            "petitioner": petitioner.strip(),
            "respondent": respondent.strip()
        })

    # Indian statutes and sections
    statute_patterns = [
        r'Section\s+\d+[A-Za-z]?\s+of\s+(?:the\s+)?[A-Z][A-Za-z \t,]+(?:Act|Code)',
        r'Article\s+\d+[A-Za-z]?\s+of\s+(?:the\s+)?Constitution',
        r'(?:IPC|CrPC|CPC|IT\s*Act|NDPS\s*Act|POCSO\s*Act)(?:\s+Section\s+\d+[A-Za-z]?)?',
        r'Order\s+[IVXLC]+\s+Rule\s+\d+',
    ]
    for pattern in statute_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        key_points["statutes"].extend(matches)

    # Judge names
    judge_patterns = [
        r"(?:Hon'?(?:ble)?\.?\s*)?(?:Justice|Judge|J\.)\s+[A-Z][A-Za-z\. \t]+",
        r"(?:Chief\s+Justice)\s+[A-Z][A-Za-z\. \t]+",
    ]
    for pattern in judge_patterns:
        matches = re.findall(pattern, text)
        key_points["judges"].extend([m.strip() for m in matches])

    # Court names
    court_patterns = [
        r'(?:Supreme\s+Court\s+of\s+India)',
        r'(?:High\s+Court\s+of\s+[A-Z][A-Za-z \t]+)',
        r'(?:District\s+Court[,\s]+[A-Z][A-Za-z \t]+)',
        r'(?:Sessions\s+Court[,\s]+[A-Z][A-Za-z \t]+)',
    ]
    for pattern in court_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        key_points["court_names"].extend(matches)

    # Key legal terms found in text
    legal_terms_list = [
        'habeas corpus', 'mandamus', 'certiorari', 'quo warranto',
        'ultra vires', 'prima facie', 'suo motu', 'locus standi',
        'res judicata', 'stare decisis', 'obiter dictum', 'ratio decidendi',
        'amicus curiae', 'interim order', 'stay order', 'bail',
        'anticipatory bail', 'writ petition', 'special leave petition',
        'fundamental rights', 'directive principles'
    ]
    text_lower = text.lower()
    for term in legal_terms_list:
        if term in text_lower:
            key_points["legal_terms"].append(term)

    # Deduplicate all lists
    for key in key_points:
        if key == "parties":
            continue
        key_points[key] = list(dict.fromkeys(key_points[key]))

    return key_points


# ── Main Summarization Function ────────────────────────────

def summarize_judgment(text, method="auto", num_sentences=5):
    """
    Summarize a legal judgment text.

    Args:
        text: The judgment text to summarize.
        method: 'abstractive', 'extractive', or 'auto' (try abstractive first).
        num_sentences: Number of sentences for extractive summary.

    Returns:
        dict with keys: summary, key_points, method, success, error
    """
    result = {
        "summary": "",
        "key_points": {},
        "method": "none",
        "success": False,
        "error": None
    }

    if not text or len(text.strip()) < 50:
        result["error"] = "Text too short for summarization (minimum 50 characters)."
        return result

    # Extract key points regardless of summarization method
    result["key_points"] = extract_key_points(text)

    try:
        if method == "abstractive" or method == "auto":
            summary = abstractive_summarize(text)
            if summary:
                result["summary"] = summary
                result["method"] = "abstractive (BART)"
                result["success"] = True
                return result

        # Fallback to extractive
        summary = extractive_summarize(text, num_sentences=num_sentences)
        if summary:
            result["summary"] = summary
            result["method"] = "extractive"
            result["success"] = True
        else:
            result["error"] = "Could not generate summary."

    except Exception as e:
        result["error"] = f"Summarization failed: {str(e)}"

    return result


def get_available_methods():
    """Return available summarization methods."""
    methods = ["extractive"]
    if HAS_TRANSFORMERS:
        methods.insert(0, "abstractive")
    methods.insert(0, "auto")
    return methods
