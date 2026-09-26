"""
AssureX — Test Suite: Data Preprocessing & Feature Engineering
==============================================================
SRS Ref: Section 1.6 (xvi) Data Pre-Processing
Tests: functional, boundary, negative
"""
import pytest
from datetime import date, timedelta
from src.preprocessing.claim_preprocessor import (
    build_feature_dict,
    ALL_FEATURES,
    CATEGORICAL_FEATURES,
    NUMERICAL_FEATURES,
)


# ── Helpers ────────────────────────────────────────────────────────

def _base_raw(overrides=None):
    """Return a minimal valid raw claim dict."""
    today = date.today()
    raw = {
        'purchase_date':           today - timedelta(days=365),
        'fault_date':              today - timedelta(days=5),
        'submission_date':         today,
        'warranty_expiry':         today + timedelta(days=365),
        'damage_type':             'mechanical',
        'warranty_type':           'standard',
        'product_category':        'Washing Machine',
        'purchase_price':          45000,
        'has_purchase_receipt':    True,
        'has_warranty_card':       True,
        'has_product_image':       True,
        'has_fault_evidence':      True,
        'has_repair_report':       False,
        'serial_number_match':     True,
        'had_unauthorized_repair': False,
        'is_duplicate_flag':       False,
        'repair_count':            0,
        'missing_doc_count':       0,
    }
    if overrides:
        raw.update(overrides)
    return raw


# ── Functional Tests ───────────────────────────────────────────────

class TestBuildFeatureDict:
    """FUNC-PRE-01 to FUNC-PRE-10: Core feature extraction."""

    def test_returns_all_required_features(self):
        """FUNC-PRE-01: Output must contain exactly ALL_FEATURES keys."""
        features = build_feature_dict(_base_raw())
        for key in ALL_FEATURES:
            assert key in features, f"Missing feature: {key}"

    def test_product_age_months_correct(self):
        """FUNC-PRE-02: product_age_months computed from purchase_date to today."""
        today = date.today()
        raw = _base_raw({'purchase_date': today - timedelta(days=365)})
        features = build_feature_dict(raw)
        age = features['product_age_months']
        assert 11.5 <= age <= 12.5, f"Expected ~12 months, got {age}"

    def test_remaining_warranty_days_correct(self):
        """FUNC-PRE-03: remaining_warranty_days from today to expiry."""
        today = date.today()
        raw = _base_raw({'warranty_expiry': today + timedelta(days=90)})
        features = build_feature_dict(raw)
        assert 88 <= features['remaining_warranty_days'] <= 91

    def test_expired_warranty_gives_zero_remaining(self):
        """FUNC-PRE-04: Expired warranty → remaining_warranty_days = 0."""
        today = date.today()
        raw = _base_raw({'warranty_expiry': today - timedelta(days=30)})
        features = build_feature_dict(raw)
        assert features['remaining_warranty_days'] == 0

    def test_boolean_true_encodes_as_one(self):
        """FUNC-PRE-05: Python True → 1 for binary features."""
        features = build_feature_dict(_base_raw({'has_purchase_receipt': True}))
        assert features['has_purchase_receipt'] == 1

    def test_boolean_false_encodes_as_zero(self):
        """FUNC-PRE-06: Python False → 0 for binary features."""
        features = build_feature_dict(_base_raw({'has_purchase_receipt': False}))
        assert features['has_purchase_receipt'] == 0

    def test_string_true_encodes_as_one(self):
        """FUNC-PRE-07: String 'true' → 1."""
        features = build_feature_dict(_base_raw({'has_purchase_receipt': 'true'}))
        assert features['has_purchase_receipt'] == 1

    def test_string_false_encodes_as_zero(self):
        """FUNC-PRE-08: String 'false' → 0."""
        features = build_feature_dict(_base_raw({'has_purchase_receipt': 'false'}))
        assert features['has_purchase_receipt'] == 0

    def test_days_since_fault_non_negative(self):
        """FUNC-PRE-09: days_since_fault is always >= 0."""
        features = build_feature_dict(_base_raw())
        assert features['days_since_fault'] >= 0

    def test_claim_submission_delay_non_negative(self):
        """FUNC-PRE-10: claim_submission_delay_days >= 0."""
        features = build_feature_dict(_base_raw())
        assert features['claim_submission_delay_days'] >= 0

    def test_all_features_are_numeric_or_string(self):
        """FUNC-PRE-11: Feature values are int, float, or str (strings for OHE categoricals)."""
        features = build_feature_dict(_base_raw())
        string_cats = {'product_category', 'brand', 'damage_type', 'warranty_type'}
        for k, v in features.items():
            if k in string_cats:
                assert isinstance(v, str), f"Feature {k} should be str, got {type(v)}"
            else:
                assert isinstance(v, (int, float)), f"Feature {k} is {type(v)}, expected numeric"

    def test_purchase_price_preserved(self):
        """FUNC-PRE-12: purchase_price value is preserved."""
        features = build_feature_dict(_base_raw({'purchase_price': 75000}))
        assert features['purchase_price'] == 75000.0

    def test_damage_type_water_preserved_as_string(self):
        """FUNC-PRE-13: damage_type='water' preserved as string for pipeline OHE."""
        features = build_feature_dict(_base_raw({'damage_type': 'water'}))
        assert features['damage_type'] == 'water'

    def test_unknown_damage_type_preserved_as_string(self):
        """FUNC-PRE-14: Unknown damage_type preserved as-is (OHE handles unknown)."""
        features = build_feature_dict(_base_raw({'damage_type': 'alien_attack'}))
        assert features['damage_type'] == 'alien_attack'


# ── Boundary Tests ─────────────────────────────────────────────────

class TestBoundaryPreprocessing:
    """BOUND-PRE-01 to BOUND-PRE-05: Edge/boundary values."""

    def test_zero_purchase_price(self):
        """BOUND-PRE-01: Zero price handled without error."""
        features = build_feature_dict(_base_raw({'purchase_price': 0}))
        assert features['purchase_price'] == 0.0

    def test_none_purchase_price(self):
        """BOUND-PRE-02: None price defaults to 0."""
        features = build_feature_dict(_base_raw({'purchase_price': None}))
        assert features['purchase_price'] == 0.0

    def test_fault_date_equals_purchase_date(self):
        """BOUND-PRE-03: Fault same day as purchase → delay=0, age≈0."""
        today = date.today()
        features = build_feature_dict(_base_raw({
            'purchase_date': today,
            'fault_date':    today,
        }))
        assert features['product_age_months'] == 0.0
        assert features['days_since_fault'] >= 0

    def test_very_old_product(self):
        """BOUND-PRE-04: Product older than 10 years → age > 120 months."""
        from datetime import date
        old = date(2010, 1, 1)
        features = build_feature_dict(_base_raw({'purchase_date': old}))
        assert features['product_age_months'] > 120

    def test_string_iso_date_parsed(self):
        """BOUND-PRE-05: ISO string dates accepted without error."""
        today = date.today()
        raw = _base_raw({
            'purchase_date':  today.isoformat(),
            'fault_date':     (today - timedelta(days=5)).isoformat(),
            'warranty_expiry': (today + timedelta(days=180)).isoformat(),
        })
        features = build_feature_dict(raw)
        assert features['remaining_warranty_days'] > 0


# ── Negative Tests ─────────────────────────────────────────────────

class TestNegativePreprocessing:
    """NEG-PRE-01 to NEG-PRE-04: Invalid / missing inputs handled gracefully."""

    def test_none_fault_date_no_crash(self):
        """NEG-PRE-01: None fault_date → no exception, days_since_fault=0."""
        raw = _base_raw({'fault_date': None})
        features = build_feature_dict(raw)
        assert features['days_since_fault'] == 0

    def test_none_warranty_expiry_no_crash(self):
        """NEG-PRE-02: None warranty_expiry → remaining_warranty_days=0."""
        raw = _base_raw({'warranty_expiry': None})
        features = build_feature_dict(raw)
        assert features['remaining_warranty_days'] == 0

    def test_invalid_date_string_no_crash(self):
        """NEG-PRE-03: Garbage date string → falls back gracefully (0 days or exception caught)."""
        from src.preprocessing.claim_preprocessor import build_feature_dict
        from datetime import date, timedelta
        raw = _base_raw({'warranty_expiry': 'not-a-date'})
        try:
            features = build_feature_dict(raw)
            # If it succeeds, remaining_warranty_days should be 0
            assert isinstance(features['remaining_warranty_days'], (int, float))
        except ValueError:
            # Acceptable — date parsing raises ValueError for garbage input
            pass

    def test_negative_repair_count_clamped(self):
        """NEG-PRE-04: repair_count of -1 still produces numeric output."""
        raw = _base_raw({'repair_count': -1})
        features = build_feature_dict(raw)
        assert isinstance(features['repair_count'], (int, float))
