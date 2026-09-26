"""
AssureX — pytest configuration and shared fixtures.
"""
import sys
import os
from pathlib import Path

# Add project root to sys.path so all src.* imports resolve correctly
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# Configure minimal Django settings so tests that touch Django-aware code work
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assurex.settings.development')

# Try to configure Django minimally — if it fails (missing deps) tests skip gracefully
try:
    import django
    from django.conf import settings
    if not settings.configured:
        settings.configure(
            DEBUG=True,
            SECRET_KEY='test-secret-key-for-pytest-only',
            INSTALLED_APPS=['django.contrib.contenttypes', 'django.contrib.auth'],
            DATABASES={'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'}},
            ML_MODEL_PATH=ROOT / 'model' / 'python_model' / 'assurex_model.pkl',
            ML_PREPROCESSOR_PATH=ROOT / 'model' / 'python_model' / 'preprocessor.pkl',
            ML_LABEL_ENCODER_PATH=ROOT / 'model' / 'python_model' / 'label_encoder.pkl',
            TM_MODEL_PATH=ROOT / 'model' / 'teachable_machine',
            WARRANTY_POLICIES_DIR=ROOT / 'policies',
            DEFAULT_CONFIDENCE_THRESHOLD=0.70,
            DEFAULT_CONFIDENCE_DIFF_STRONG=5.0,
            DEFAULT_CONFIDENCE_DIFF_ACCEPTABLE=15.0,
            DEFAULT_CONFIDENCE_DIFF_WEAK=25.0,
            WARRANTY_EXPIRY_ALERT_DAYS=30,
        )
    DJANGO_AVAILABLE = True
except Exception:
    DJANGO_AVAILABLE = False

# ──────────────────────────────────────────────────────────────────────────────
# Shared pytest fixtures (no Django dependency)
# ──────────────────────────────────────────────────────────────────────────────
import pytest
from datetime import date, timedelta


@pytest.fixture
def valid_claim_data():
    """Feature dict for a textbook valid claim."""
    today = date.today()
    return {
        'purchase_date':                (today - timedelta(days=180)).isoformat(),
        'fault_date':                   (today - timedelta(days=5)).isoformat(),
        'submission_date':               today.isoformat(),
        'warranty_expiry':              (today + timedelta(days=185)).isoformat(),
        'damage_type':                  'mechanical',
        'warranty_type':                'standard',
        'product_category':             'Washing Machine',
        'purchase_price':               45000,
        'has_purchase_receipt':         True,
        'has_warranty_card':            True,
        'has_product_image':            True,
        'has_fault_evidence':           True,
        'has_repair_report':            False,
        'serial_number_match':          True,
        'had_unauthorized_repair':      False,
        'is_duplicate_flag':            False,
        'repair_count':                 0,
        'missing_doc_count':            0,
    }


@pytest.fixture
def invalid_claim_data():
    """Feature dict for a clearly invalid claim (expired warranty)."""
    today = date.today()
    return {
        'purchase_date':                (today - timedelta(days=730)).isoformat(),
        'fault_date':                   (today - timedelta(days=5)).isoformat(),
        'submission_date':               today.isoformat(),
        'warranty_expiry':              (today - timedelta(days=365)).isoformat(),  # EXPIRED
        'damage_type':                  'water',         # excluded damage
        'warranty_type':                'standard',
        'product_category':             'Smartphone',
        'purchase_price':               30000,
        'has_purchase_receipt':         False,           # missing receipt
        'has_warranty_card':            False,
        'has_product_image':            False,
        'has_fault_evidence':           False,
        'has_repair_report':            False,
        'serial_number_match':          False,           # mismatch
        'had_unauthorized_repair':      True,
        'is_duplicate_flag':            True,
        'repair_count':                 3,               # too many
        'missing_doc_count':            5,
    }


@pytest.fixture
def manual_review_data():
    """Feature dict for a borderline manual-review claim."""
    today = date.today()
    return {
        'purchase_date':                (today - timedelta(days=350)).isoformat(),
        'fault_date':                   (today - timedelta(days=10)).isoformat(),
        'submission_date':               today.isoformat(),
        'warranty_expiry':              (today + timedelta(days=15)).isoformat(),  # expiring soon
        'damage_type':                  'electrical',
        'warranty_type':                'extended',
        'product_category':             'Television',
        'purchase_price':               60000,
        'has_purchase_receipt':         True,
        'has_warranty_card':            False,           # missing one doc
        'has_product_image':            True,
        'has_fault_evidence':           True,
        'has_repair_report':            False,
        'serial_number_match':          True,
        'had_unauthorized_repair':      False,
        'is_duplicate_flag':            False,
        'repair_count':                 1,
        'missing_doc_count':            1,
    }


@pytest.fixture
def sample_card_image(tmp_path):
    """Generate a minimal claim card PNG for TM model tests."""
    from PIL import Image
    img_path = tmp_path / 'test_card.png'
    # Create a simple 64×64 white image
    Image.new('RGB', (64, 64), color='white').save(str(img_path))
    return str(img_path)
