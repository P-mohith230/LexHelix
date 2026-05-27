"""
Module 1: OCR Image Text Extractor
Extracts text from scanned legal document images using Tesseract OCR.
Includes image preprocessing for better accuracy.
"""

import os
import re

try:
    import pytesseract
    from PIL import Image, ImageFilter, ImageEnhance
    HAS_TESSERACT = True
except ImportError:
    HAS_TESSERACT = False

try:
    import cv2
    import numpy as np
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False


# ── Configuration ──────────────────────────────────────────

SUPPORTED_FORMATS = {'.png', '.jpg', '.jpeg', '.tiff', '.tif', '.bmp', '.webp'}

# Windows Tesseract default path
if os.name == 'nt':
    tesseract_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    if os.path.exists(tesseract_path) and HAS_TESSERACT:
        pytesseract.pytesseract.tesseract_cmd = tesseract_path


# ── Preprocessing ──────────────────────────────────────────

def preprocess_with_pil(image):
    """Basic preprocessing using Pillow."""
    # Convert to grayscale
    gray = image.convert('L')

    # Enhance contrast
    enhancer = ImageEnhance.Contrast(gray)
    enhanced = enhancer.enhance(2.0)

    # Enhance sharpness
    enhancer = ImageEnhance.Sharpness(enhanced)
    enhanced = enhancer.enhance(2.0)

    # Apply threshold (binarize)
    threshold = 140
    binary = enhanced.point(lambda x: 255 if x > threshold else 0, '1')

    return binary


def preprocess_with_cv2(image_path):
    """Advanced preprocessing using OpenCV."""
    img = cv2.imread(image_path)
    if img is None:
        return None

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Noise removal with Gaussian blur
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)

    # Adaptive thresholding for varying lighting conditions
    binary = cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 11, 2
    )

    # Deskew the image
    coords = np.column_stack(np.where(binary > 0))
    if len(coords) > 5:
        angle = cv2.minAreaRect(coords)[-1]
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
        if abs(angle) > 0.5:
            (h, w) = binary.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            binary = cv2.warpAffine(
                binary, M, (w, h),
                flags=cv2.INTER_CUBIC,
                borderMode=cv2.BORDER_REPLICATE
            )

    # Morphological operations to clean up
    kernel = np.ones((1, 1), np.uint8)
    binary = cv2.dilate(binary, kernel, iterations=1)
    binary = cv2.erode(binary, kernel, iterations=1)

    return binary


# ── Main OCR Function ─────────────────────────────────────

def extract_text(image_path):
    """
    Extract text from a scanned document image.

    Args:
        image_path: Path to the image file.

    Returns:
        dict with keys: text, confidence, word_count, method, success, error
    """
    result = {
        "text": "",
        "confidence": 0.0,
        "word_count": 0,
        "method": "none",
        "success": False,
        "error": None
    }

    # Validate file
    if not os.path.exists(image_path):
        result["error"] = f"File not found: {image_path}"
        return result

    ext = os.path.splitext(image_path)[1].lower()
    if ext not in SUPPORTED_FORMATS:
        result["error"] = f"Unsupported format: {ext}. Supported: {', '.join(SUPPORTED_FORMATS)}"
        return result

    if not HAS_TESSERACT:
        result["error"] = "pytesseract not installed. Run: pip install pytesseract"
        return result

    try:
        # Try OpenCV preprocessing first (better quality)
        if HAS_CV2:
            preprocessed = preprocess_with_cv2(image_path)
            if preprocessed is not None:
                # Get detailed OCR data
                data = pytesseract.image_to_data(
                    preprocessed, output_type=pytesseract.Output.DICT,
                    config='--oem 3 --psm 6'
                )
                result["method"] = "opencv+tesseract"
            else:
                # Fallback to PIL
                image = Image.open(image_path)
                preprocessed = preprocess_with_pil(image)
                data = pytesseract.image_to_data(
                    preprocessed, output_type=pytesseract.Output.DICT,
                    config='--oem 3 --psm 6'
                )
                result["method"] = "pil+tesseract"
        else:
            # PIL-only preprocessing
            image = Image.open(image_path)
            preprocessed = preprocess_with_pil(image)
            data = pytesseract.image_to_data(
                preprocessed, output_type=pytesseract.Output.DICT,
                config='--oem 3 --psm 6'
            )
            result["method"] = "pil+tesseract"

        # Extract text and calculate confidence
        words = []
        confidences = []
        for i, word in enumerate(data['text']):
            word = word.strip()
            if word:
                words.append(word)
                conf = int(data['conf'][i])
                if conf > 0:
                    confidences.append(conf)

        result["text"] = ' '.join(words)
        result["word_count"] = len(words)
        result["confidence"] = round(
            sum(confidences) / len(confidences), 2
        ) if confidences else 0.0
        result["success"] = True

    except pytesseract.TesseractNotFoundError:
        result["error"] = (
            "Tesseract not found. Install from: "
            "https://github.com/UB-Mannheim/tesseract/wiki"
        )
    except Exception as e:
        result["error"] = f"OCR extraction failed: {str(e)}"

    return result


def extract_text_simple(image_path):
    """
    Simple text extraction without detailed confidence data.
    Faster but less information.
    """
    if not HAS_TESSERACT:
        return "Error: pytesseract not installed."

    try:
        image = Image.open(image_path)
        preprocessed = preprocess_with_pil(image)
        text = pytesseract.image_to_string(preprocessed, config='--oem 3 --psm 6')
        return clean_text(text)
    except Exception as e:
        return f"Error: {str(e)}"


# ── Text Cleaning ──────────────────────────────────────────

def clean_text(text):
    """Clean and normalize OCR-extracted text."""
    if not text:
        return ""

    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)

    # Remove common OCR artifacts
    text = re.sub(r'[|}{~`]', '', text)

    # Fix common OCR misreads in legal text
    text = text.replace('  ', ' ')
    text = text.replace(' .', '.')
    text = text.replace(' ,', ',')

    # Normalize quotes
    text = text.replace('"', '"').replace('"', '"')
    text = text.replace(''', "'").replace(''', "'")

    return text.strip()


# ── Utility ────────────────────────────────────────────────

def is_tesseract_available():
    """Check if Tesseract OCR is available."""
    if not HAS_TESSERACT:
        return False
    try:
        pytesseract.get_tesseract_version()
        return True
    except Exception:
        return False


def get_supported_formats():
    """Return set of supported image formats."""
    return SUPPORTED_FORMATS
