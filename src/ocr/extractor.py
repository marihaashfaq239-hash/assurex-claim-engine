"""
AssureX — OCR Extractor
Extracts structured data from uploaded receipts, warranty cards, and documents.
Supports both Tesseract and EasyOCR as fallback.
"""
from __future__ import annotations
import os
import re
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────
# Tesseract wrapper
# ─────────────────────────────────────────────────────────────────

def _tesseract_extract(image_path: str) -> str:
    """Extract raw text using Tesseract OCR."""
    try:
        import pytesseract
        from PIL import Image
        from django.conf import settings

        tesseract_path = getattr(settings, 'TESSERACT_PATH', None)
        if tesseract_path and os.path.exists(tesseract_path):
            pytesseract.pytesseract.tesseract_cmd = tesseract_path

        img  = Image.open(image_path)
        text = pytesseract.image_to_string(img, config='--psm 6')
        return text
    except Exception as e:
        logger.warning(f'Tesseract failed: {e}')
        return ''


def _easyocr_extract(image_path: str) -> str:
    """Extract raw text using EasyOCR (fallback)."""
    try:
        import easyocr
        reader = easyocr.Reader(['en'], gpu=False)
        results = reader.readtext(image_path, detail=0)
        return '\n'.join(results)
    except Exception as e:
        logger.warning(f'EasyOCR failed: {e}')
        return ''


def extract_text(file_path: str) -> tuple[str, str]:
    """
    Extract raw text from an image or PDF file.
    Returns (raw_text, engine_used).
    """
    path = str(file_path)
    ext  = Path(path).suffix.lower()

    # For PDF, extract first page as image
    if ext == '.pdf':
        try:
            import fitz   # PyMuPDF
            doc  = fitz.open(path)
            page = doc[0]
            pix  = page.get_pixmap(dpi=200)
            tmp  = path + '_page0.png'
            pix.save(tmp)
            path = tmp
        except Exception as e:
            logger.warning(f'PDF to image failed: {e}')
            return '', 'none'

    # Try Tesseract first, then EasyOCR
    text = _tesseract_extract(path)
    if len(text.strip()) > 20:
        return text, 'tesseract'

    text = _easyocr_extract(path)
    if len(text.strip()) > 20:
        return text, 'easyocr'

    return text, 'none'


# ─────────────────────────────────────────────────────────────────
# Field parsers
# ─────────────────────────────────────────────────────────────────

_DATE_PATTERNS = [
    r'(\d{2}[/-]\d{2}[/-]\d{4})',   # DD/MM/YYYY or DD-MM-YYYY
    r'(\d{4}[/-]\d{2}[/-]\d{2})',   # YYYY-MM-DD
    r'(\d{2}\s+\w+\s+\d{4})',       # 10 Jan 2024
    r'(\w+\s+\d{2},?\s+\d{4})',     # January 10, 2024
]

_DATE_FORMATS = [
    '%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d', '%Y/%m/%d',
    '%d %b %Y', '%d %B %Y', '%B %d, %Y', '%b %d, %Y',
    '%d %b, %Y',
]


def _parse_date(text: str) -> Optional[str]:
    """Find and parse a date string, returns ISO format YYYY-MM-DD or None."""
    for pattern in _DATE_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for m in matches:
            for fmt in _DATE_FORMATS:
                try:
                    dt = datetime.strptime(m.strip(), fmt)
                    return dt.strftime('%Y-%m-%d')
                except ValueError:
                    continue
    return None


def _parse_amount(text: str) -> Optional[float]:
    """Extract monetary amount from text."""
    # Look for PKR, Rs, amount patterns
    patterns = [
        r'(?:PKR|Rs\.?|₨)\s*([\d,]+(?:\.\d{2})?)',
        r'([\d,]+(?:\.\d{2})?)\s*(?:PKR|Rs\.?)',
        r'(?:Amount|Price|Total)[:\s]+([\d,]+(?:\.\d{2})?)',
    ]
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            try:
                return float(m.group(1).replace(',', ''))
            except ValueError:
                continue
    return None


def _parse_serial(text: str) -> Optional[str]:
    """Extract serial number from text."""
    patterns = [
        r'(?:Serial\s*(?:No\.?|Number)?|S/?N)[:\s#]*([A-Z0-9\-]{6,25})',
        r'(?:SN|S\.N\.)[:\s]*([A-Z0-9\-]{6,25})',
    ]
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            return m.group(1).strip()
    return None


def _parse_invoice_number(text: str) -> Optional[str]:
    patterns = [
        r'(?:Invoice|Inv\.?|Bill)\s*(?:No\.?|Number|#)[:\s]*([A-Z0-9\-/]{4,20})',
        r'(?:Receipt|Rcpt)\s*(?:No\.?|#)[:\s]*([A-Z0-9\-/]{4,20})',
    ]
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            return m.group(1).strip()
    return None


def _parse_model_number(text: str) -> Optional[str]:
    patterns = [
        r'(?:Model\s*(?:No\.?|Number)?)[:\s]*([A-Z0-9\-/]{4,25})',
        r'(?:Part\s*No\.?)[:\s]*([A-Z0-9\-/]{4,25})',
    ]
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            return m.group(1).strip()
    return None


def _parse_retailer(text: str) -> Optional[str]:
    patterns = [
        r'(?:Sold\s+by|Retailer|Dealer|Shop)[:\s]+([A-Za-z0-9\s&\.]+?)(?:\n|,|Tel|Phone)',
        r'(?:Store|Outlet)[:\s]+([A-Za-z0-9\s&\.]+?)(?:\n|,)',
    ]
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            return m.group(1).strip()[:100]
    return None


def _parse_warranty_duration(text: str) -> Optional[str]:
    patterns = [
        r'(\d+)\s*(?:Year|Yr)s?\s*(?:Warranty|Guarantee)',
        r'(\d+)\s*(?:Month)s?\s*(?:Warranty|Guarantee)',
        r'Warranty[:\s]+(\d+\s*(?:Year|Month)s?)',
    ]
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            return m.group(1).strip() if len(m.groups()) == 1 else m.group(0).strip()
    return None


# ─────────────────────────────────────────────────────────────────
# Main extraction function
# ─────────────────────────────────────────────────────────────────

def extract_document_data(file_path: str) -> dict:
    """
    Full OCR pipeline: extract text → parse fields → return structured dict.

    Returns:
        {
            'raw_text': str,
            'engine': str,
            'invoice_number': str | None,
            'purchase_date': str | None,    # ISO date
            'serial_number': str | None,
            'model_number': str | None,
            'purchase_amount': float | None,
            'retailer': str | None,
            'warranty_duration': str | None,
            'confidence': float,            # 0-1
        }
    """
    raw_text, engine = extract_text(file_path)

    if not raw_text.strip():
        return {
            'raw_text': '', 'engine': engine,
            'invoice_number': None, 'purchase_date': None,
            'serial_number': None, 'model_number': None,
            'purchase_amount': None, 'retailer': None,
            'warranty_duration': None, 'confidence': 0.0,
        }

    # Parse individual fields
    invoice    = _parse_invoice_number(raw_text)
    date       = _parse_date(raw_text)
    serial     = _parse_serial(raw_text)
    model_no   = _parse_model_number(raw_text)
    amount     = _parse_amount(raw_text)
    retailer   = _parse_retailer(raw_text)
    warranty   = _parse_warranty_duration(raw_text)

    # Compute confidence: proportion of fields extracted
    fields     = [invoice, date, serial, model_no, amount, retailer]
    found      = sum(1 for f in fields if f is not None)
    confidence = round(found / len(fields), 2)

    return {
        'raw_text':         raw_text,
        'engine':           engine,
        'invoice_number':   invoice,
        'purchase_date':    date,
        'serial_number':    serial,
        'model_number':     model_no,
        'purchase_amount':  amount,
        'retailer':         retailer,
        'warranty_duration':warranty,
        'confidence':       confidence,
    }
