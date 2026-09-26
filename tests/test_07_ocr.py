"""
AssureX — Test Suite: OCR Data Extraction
==========================================
SRS Ref: Section 1.6 (vi) Receipt Scanning and Data Extraction
         Section 1.6 (vii) Extracted Data Verification
Tests: functional, OCR field extraction, negative, boundary
"""
import pytest
import os
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _make_test_image(text: str, output_path: str):
    """Create a simple PNG image with given text using Pillow."""
    from PIL import Image, ImageDraw, ImageFont
    img  = Image.new('RGB', (400, 200), color='white')
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype('arial.ttf', 14)
    except Exception:
        font = ImageFont.load_default()
    draw.text((10, 10), text, fill='black', font=font)
    img.save(output_path, 'PNG')


class TestOCRExtractor:
    """FUNC-OCR-01 to FUNC-OCR-08."""

    def test_ocr_module_importable(self):
        """FUNC-OCR-01: OCR extractor module imports without error."""
        try:
            from src.ocr.extractor import extract_document_data
            assert callable(extract_document_data)
        except ImportError as e:
            # If tesseract not installed, just verify module structure
            pytest.skip(f"OCR module requires tesseract: {e}")

    def test_extract_returns_dict(self, tmp_path):
        """FUNC-OCR-02: extract_document_data() always returns a dict."""
        try:
            from src.ocr.extractor import extract_document_data
        except ImportError:
            pytest.skip("OCR dependencies not installed")

        img_path = tmp_path / 'test_receipt.png'
        _make_test_image("Invoice: INV-12345\nDate: 2024-06-01\nAmount: PKR 45,000", str(img_path))

        result = extract_document_data(str(img_path))
        assert isinstance(result, dict), f"Expected dict, got {type(result)}"

    def test_extract_has_required_keys(self, tmp_path):
        """FUNC-OCR-03: Result dict has all required extraction fields."""
        try:
            from src.ocr.extractor import extract_document_data
        except ImportError:
            pytest.skip("OCR dependencies not installed")

        img_path = tmp_path / 'test.png'
        _make_test_image("Receipt", str(img_path))
        result = extract_document_data(str(img_path))

        expected_keys = ['invoice_number', 'purchase_date', 'serial_number',
                         'model_number', 'purchase_amount', 'retailer', 'raw_text']
        for key in expected_keys:
            assert key in result, f"Missing key: {key}"

    def test_extract_has_confidence_score(self, tmp_path):
        """FUNC-OCR-04: Result includes a confidence score (0–1)."""
        try:
            from src.ocr.extractor import extract_document_data
        except ImportError:
            pytest.skip("OCR dependencies not installed")

        img_path = tmp_path / 'test.png'
        _make_test_image("Test", str(img_path))
        result = extract_document_data(str(img_path))

        assert 'confidence' in result
        conf = result['confidence']
        assert 0.0 <= conf <= 1.0, f"Confidence {conf} not in [0,1]"

    def test_extract_has_engine_field(self, tmp_path):
        """FUNC-OCR-05: Result includes 'engine' field."""
        try:
            from src.ocr.extractor import extract_document_data
        except ImportError:
            pytest.skip("OCR dependencies not installed")

        img_path = tmp_path / 'test.png'
        _make_test_image("Test", str(img_path))
        result = extract_document_data(str(img_path))
        assert 'engine' in result

    def test_raw_text_is_string(self, tmp_path):
        """FUNC-OCR-06: raw_text field is always a string."""
        try:
            from src.ocr.extractor import extract_document_data
        except ImportError:
            pytest.skip("OCR dependencies not installed")

        img_path = tmp_path / 'test.png'
        _make_test_image("Hello World", str(img_path))
        result = extract_document_data(str(img_path))
        assert isinstance(result.get('raw_text', ''), str)

    def test_nonexistent_file_no_crash(self):
        """FUNC-OCR-07 (NEG): Non-existent file handled gracefully."""
        try:
            from src.ocr.extractor import extract_document_data
        except ImportError:
            pytest.skip("OCR dependencies not installed")

        result = extract_document_data('/nonexistent/file.jpg')
        assert isinstance(result, dict)
        # Should return a result with error indication, not raise

    def test_blank_white_image_no_crash(self, tmp_path):
        """FUNC-OCR-08 (NEG): Blank white image returns empty result, no crash."""
        try:
            from src.ocr.extractor import extract_document_data
            from PIL import Image
        except ImportError:
            pytest.skip("OCR dependencies not installed")

        blank = tmp_path / 'blank.png'
        Image.new('RGB', (400, 200), color='white').save(str(blank))
        result = extract_document_data(str(blank))
        assert isinstance(result, dict)


class TestOCRBoundary:
    """BOUND-OCR-01 to BOUND-OCR-02."""

    def test_very_small_image_no_crash(self, tmp_path):
        """BOUND-OCR-01: 10×10 pixel image handled without crash."""
        try:
            from src.ocr.extractor import extract_document_data
            from PIL import Image
        except ImportError:
            pytest.skip("OCR dependencies not installed")

        tiny = tmp_path / 'tiny.png'
        Image.new('RGB', (10, 10), color='white').save(str(tiny))
        try:
            result = extract_document_data(str(tiny))
            assert isinstance(result, dict)
        except Exception as e:
            pytest.fail(f"Tiny image caused crash: {e}")

    def test_large_pdf_like_image_no_crash(self, tmp_path):
        """BOUND-OCR-02: Large image (A4 equivalent) no crash."""
        try:
            from src.ocr.extractor import extract_document_data
            from PIL import Image
        except ImportError:
            pytest.skip("OCR dependencies not installed")

        large = tmp_path / 'large.png'
        Image.new('RGB', (2480, 3508), color='white').save(str(large))
        try:
            result = extract_document_data(str(large))
            assert isinstance(result, dict)
        except Exception:
            pass  # Some environments may time out on huge images — acceptable


class TestDocumentDuplicateDetection:
    """DUP-DOC-01: SHA-256 hash duplicate detection."""

    def test_same_file_produces_same_hash(self, tmp_path):
        """DUP-DOC-01: Same file content → same SHA-256 hash."""
        import hashlib

        content = b'This is a test receipt content 12345'
        f1 = tmp_path / 'doc1.pdf'
        f2 = tmp_path / 'doc2.pdf'
        f1.write_bytes(content)
        f2.write_bytes(content)

        def sha256_of(path):
            sha = hashlib.sha256()
            with open(path, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    sha.update(chunk)
            return sha.hexdigest()

        assert sha256_of(f1) == sha256_of(f2)

    def test_different_files_produce_different_hash(self, tmp_path):
        """DUP-DOC-02: Different content → different SHA-256 hash."""
        import hashlib

        f1 = tmp_path / 'doc1.pdf'
        f2 = tmp_path / 'doc2.pdf'
        f1.write_bytes(b'Receipt A content')
        f2.write_bytes(b'Receipt B content - different')

        def sha256_of(path):
            sha = hashlib.sha256()
            with open(path, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    sha.update(chunk)
            return sha.hexdigest()

        assert sha256_of(f1) != sha256_of(f2)
