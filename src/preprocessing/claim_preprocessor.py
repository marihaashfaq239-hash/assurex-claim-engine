"""
AssureX — Claim Data Preprocessor
Cleans and transforms raw claim data into ML-ready feature vectors.
Used for both training (dataset_generator) and inference (claim submission).
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from datetime import date, datetime
from typing import Optional, Union
import logging

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────
# Feature definitions (must match training dataset columns exactly)
# ─────────────────────────────────────────────────────────────────

# NOTE: Feature order must exactly match src/ml/train_model.py ALL_FEATURES
# The trained model (assurex_model.pkl) was built with these exact columns.
ALL_FEATURES = [
    'product_category', 'brand', 'damage_type', 'warranty_type',
    'product_age_months', 'remaining_warranty_days', 'days_since_fault',
    'claim_submission_delay_days', 'purchase_price', 'repair_count',
    'missing_doc_count', 'has_purchase_receipt', 'has_warranty_card',
    'has_product_image', 'has_fault_evidence', 'has_repair_report',
    'serial_number_match', 'had_unauthorized_repair', 'is_duplicate_flag',
]

# Logical groupings (used by notebooks and test helpers)
CATEGORICAL_FEATURES = [
    'product_category', 'brand', 'damage_type', 'warranty_type',
    'has_purchase_receipt', 'has_warranty_card', 'has_product_image',
    'has_fault_evidence', 'has_repair_report', 'serial_number_match',
    'had_unauthorized_repair', 'is_duplicate_flag',
]

NUMERICAL_FEATURES = [
    'product_age_months', 'remaining_warranty_days', 'days_since_fault',
    'claim_submission_delay_days', 'repair_count', 'missing_doc_count',
    'purchase_price',
]

DAMAGE_TYPE_MAP = {
    'physical': 0, 'electrical': 1, 'mechanical': 2, 'software': 3,
    'manufacturing': 4, 'water': 5, 'overheating': 6, 'battery': 7,
    'display': 8, 'other': 9,
}

WARRANTY_TYPE_MAP = {
    'standard': 0, 'extended': 1, 'third_party': 2,
}

CATEGORY_MAP = {
    'Air Conditioner': 0, 'Refrigerator': 1, 'Washing Machine': 2,
    'Television': 3, 'Smartphone': 4, 'Laptop': 5, 'Microwave': 6,
    'Generator': 7, 'Water Heater': 8, 'Small Appliance': 9,
}

LABEL_MAP = {
    'valid_claim': 0, 'invalid_claim': 1, 'manual_review': 2,
}
LABEL_MAP_REVERSE = {v: k for k, v in LABEL_MAP.items()}


def _safe_days(d1, d2) -> int:
    """Return (d2 - d1).days safely, handling None/string inputs."""
    try:
        if isinstance(d1, str):
            d1 = datetime.strptime(d1[:10], '%Y-%m-%d').date()
        if isinstance(d2, str):
            d2 = datetime.strptime(d2[:10], '%Y-%m-%d').date()
        if d1 is None or d2 is None:
            return 0
        return max(0, (d2 - d1).days)
    except Exception:
        return 0


def build_feature_dict(claim_data: dict) -> dict:
    """
    Converts a raw claim dictionary into a normalized feature dictionary.

    claim_data keys expected:
        purchase_date, fault_date, submission_date, warranty_start, warranty_expiry,
        damage_type, warranty_type, product_category, purchase_price,
        has_purchase_receipt, has_warranty_card, has_product_image,
        has_fault_evidence, has_repair_report,
        serial_number_match, had_unauthorized_repair, is_duplicate_flag,
        repair_count, missing_doc_count
    """
    today = date.today()

    # ── Date-derived features ──
    purchase_date   = claim_data.get('purchase_date')
    fault_date      = claim_data.get('fault_date')
    submission_date = claim_data.get('submission_date') or today
    warranty_expiry = claim_data.get('warranty_expiry')

    product_age_months = round(_safe_days(purchase_date, today) / 30.44, 1)

    remaining_warranty_days = 0
    if warranty_expiry:
        exp = warranty_expiry
        if isinstance(exp, str):
            exp = datetime.strptime(exp[:10], '%Y-%m-%d').date()
        remaining_warranty_days = max(0, (exp - today).days)

    days_since_fault = _safe_days(fault_date, today) if fault_date else 0
    claim_submission_delay = _safe_days(fault_date, submission_date) if fault_date else 0

    # ── Categorical encoding ──
    damage_type     = DAMAGE_TYPE_MAP.get(claim_data.get('damage_type', ''), 9)
    warranty_type   = WARRANTY_TYPE_MAP.get(claim_data.get('warranty_type', 'standard'), 0)
    product_category = CATEGORY_MAP.get(claim_data.get('product_category', ''), 9)

    # ── Boolean features → int ──
    def _bool(val) -> int:
        if isinstance(val, bool):
            return int(val)
        if isinstance(val, str):
            return 1 if val.lower() in ('true', 'yes', '1') else 0
        return int(bool(val))

    features = {
        # Categorical (string — passed through pipeline's OHE)
        'product_category':       claim_data.get('product_category', 'Small Appliance') or 'Small Appliance',
        'brand':                  claim_data.get('brand', 'Other') or 'Other',
        'damage_type':            claim_data.get('damage_type', 'other') or 'other',
        'warranty_type':          claim_data.get('warranty_type', 'standard') or 'standard',
        # Binary (0/1)
        'has_purchase_receipt':   _bool(claim_data.get('has_purchase_receipt', False)),
        'has_warranty_card':      _bool(claim_data.get('has_warranty_card', False)),
        'has_product_image':      _bool(claim_data.get('has_product_image', False)),
        'has_fault_evidence':     _bool(claim_data.get('has_fault_evidence', False)),
        'has_repair_report':      _bool(claim_data.get('has_repair_report', False)),
        'serial_number_match':    _bool(claim_data.get('serial_number_match', True)),
        'had_unauthorized_repair':_bool(claim_data.get('had_unauthorized_repair', False)),
        'is_duplicate_flag':      _bool(claim_data.get('is_duplicate_flag', False)),
        # Numerical
        'product_age_months':           product_age_months,
        'remaining_warranty_days':      remaining_warranty_days,
        'days_since_fault':             days_since_fault,
        'claim_submission_delay_days':  claim_submission_delay,
        'repair_count':                 int(claim_data.get('repair_count', 0)),
        'missing_doc_count':            int(claim_data.get('missing_doc_count', 0)),
        'purchase_price':               float(claim_data.get('purchase_price', 0) or 0),
    }
    return features


def features_to_dataframe(feature_dict: dict) -> pd.DataFrame:
    """Convert a single feature dict to a single-row DataFrame (for model input)."""
    return pd.DataFrame([feature_dict])[ALL_FEATURES]


def extract_claim_features(claim) -> dict:
    """
    Convenience: extract feature dict directly from a Claim ORM instance.
    Imports apps here to avoid circular imports at module load.
    """
    from apps.claims.models import ClaimDocument

    docs = claim.documents.all()
    doc_types = set(docs.values_list('doc_type', flat=True))
    repairs = list(claim.repair_history.all())

    # Check serial number match against OCR results
    serial_match = True
    ocr_qs = claim.ocr_results.filter(serial_number__isnull=False).exclude(serial_number='')
    if ocr_qs.exists():
        ocr_serial = ocr_qs.first().serial_number.strip().upper()
        claim_serial = claim.product.serial_number.strip().upper()
        serial_match = ocr_serial == claim_serial

    warranty = claim.warranty
    warranty_expiry  = warranty.expiry_date if warranty else None
    warranty_type    = warranty.warranty_type if warranty else 'standard'
    product_category = claim.product.category.name if claim.product.category else ''
    purchase_date    = claim.product.purchase_date
    purchase_price   = float(claim.product.purchase_price or 0)

    missing_docs = len(claim.missing_document_types)

    raw = {
        'purchase_date':         purchase_date,
        'fault_date':            claim.fault_date,
        'submission_date':       claim.submission_date.date() if claim.submission_date else None,
        'warranty_expiry':       warranty_expiry,
        'product_category':      product_category,
        'brand':                 getattr(claim.product, 'brand', 'Other') or 'Other',
        'damage_type':           claim.damage_type,
        'warranty_type':         warranty_type,
        'purchase_price':        purchase_price,
        'has_purchase_receipt':  'purchase_receipt' in doc_types,
        'has_warranty_card':     'warranty_card' in doc_types,
        'has_product_image':     'product_image' in doc_types,
        'has_fault_evidence':    'fault_evidence' in doc_types,
        'has_repair_report':     'repair_report' in doc_types,
        'serial_number_match':   serial_match,
        'had_unauthorized_repair': any(not r.is_authorized for r in repairs),
        'is_duplicate_flag':     claim.is_duplicate,
        'repair_count':          len(repairs),
        'missing_doc_count':     missing_docs,
    }
    return build_feature_dict(raw)
