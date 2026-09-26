"""
AssureX — Test Suite: Python ML Classification Model
=====================================================
SRS Ref: Section 1.6 (xviii–xix) Python Classification Model,
         Python Confidence Score Generation
Tests: functional, boundary, negative, model accuracy
"""
import pytest
from pathlib import Path
from datetime import date, timedelta

ROOT       = Path(__file__).resolve().parent.parent
MODEL_PATH = ROOT / 'model' / 'python_model' / 'assurex_model.pkl'
LE_PATH    = ROOT / 'model' / 'python_model' / 'label_encoder.pkl'
MODEL_AVAILABLE = MODEL_PATH.exists() and LE_PATH.exists()

skip_if_no_model = pytest.mark.skipif(
    not MODEL_AVAILABLE,
    reason="Python model files not found — run src/ml/train_model.py first"
)


# ── Direct predictor that doesn't require Django settings ──────────

def _predict(feature_dict: dict) -> dict:
    """Call prediction directly (no Django settings dependency)."""
    import numpy as np
    import pandas as pd
    import joblib
    from src.ml.train_model import ALL_FEATURES  # use model's feature list

    if not MODEL_PATH.exists():
        from src.ml.predictor import _mock_prediction
        return _mock_prediction()

    pipeline = joblib.load(str(MODEL_PATH))
    le       = joblib.load(str(LE_PATH))
    df       = pd.DataFrame([feature_dict])
    # Fill missing columns with defaults
    for col in ALL_FEATURES:
        if col not in df.columns:
            df[col] = 'Other' if col in ('brand', 'product_category', 'damage_type', 'warranty_type') else 0
    df      = df[ALL_FEATURES]
    proba   = pipeline.predict_proba(df)[0]
    pred_i  = int(np.argmax(proba))
    classes = le.classes_
    pred    = le.inverse_transform([pred_i])[0]
    conf    = {cls: round(float(p) * 100, 2) for cls, p in zip(classes, proba)}
    return {
        'predicted_class':    pred,
        'confidence_valid':   conf.get('valid_claim',   0.0),
        'confidence_invalid': conf.get('invalid_claim', 0.0),
        'confidence_manual':  conf.get('manual_review', 0.0),
        'top_confidence':     round(float(max(proba)) * 100, 2),
        'processing_time_ms': 0,
        'model_version':      'assurex_v1',
        'error':              None,
    }


def _features(overrides=None):
    today = date.today()
    base = {
        'purchase_date':                today - timedelta(days=180),
        'fault_date':                   today - timedelta(days=5),
        'submission_date':              today,
        'warranty_expiry':              today + timedelta(days=185),
        'product_category':             'Washing Machine',
        'brand':                        'Samsung',
        'damage_type':                  'mechanical',
        'warranty_type':                'standard',
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
    if overrides:
        base.update(overrides)
    from src.preprocessing.claim_preprocessor import build_feature_dict
    return build_feature_dict(base)


# ── Functional Tests ───────────────────────────────────────────────

class TestPythonModelPredictor:
    """FUNC-PY-01 to FUNC-PY-12."""

    def test_predictor_import(self):
        """FUNC-PY-01: predictor module imports without error."""
        from src.ml.predictor import run_python_ml_prediction
        assert callable(run_python_ml_prediction)

    @skip_if_no_model
    def test_prediction_returns_dict(self):
        """FUNC-PY-02: Prediction returns a dict."""
        result = _predict(_features())
        assert isinstance(result, dict)

    @skip_if_no_model
    def test_prediction_has_required_keys(self):
        """FUNC-PY-03: Result dict has all required keys."""
        result = _predict(_features())
        for key in ['predicted_class', 'confidence_valid', 'confidence_invalid',
                    'confidence_manual', 'top_confidence']:
            assert key in result, f"Missing key: {key}"

    @skip_if_no_model
    def test_predicted_class_is_one_of_three(self):
        """FUNC-PY-04: predicted_class is valid class name."""
        result = _predict(_features())
        assert result['predicted_class'] in ('valid_claim', 'invalid_claim', 'manual_review')

    @skip_if_no_model
    def test_confidence_scores_sum_to_100(self):
        """FUNC-PY-05: Three confidence scores sum to ~100%."""
        result = _predict(_features())
        total = result['confidence_valid'] + result['confidence_invalid'] + result['confidence_manual']
        assert abs(total - 100.0) < 1.0, f"Confidence scores sum to {total}, expected ~100"

    @skip_if_no_model
    def test_confidence_scores_non_negative(self):
        """FUNC-PY-06: All confidence scores >= 0."""
        result = _predict(_features())
        assert result['confidence_valid']   >= 0
        assert result['confidence_invalid'] >= 0
        assert result['confidence_manual']  >= 0

    @skip_if_no_model
    def test_top_confidence_matches_predicted_class(self):
        """FUNC-PY-07: top_confidence equals the max of the three confidence scores."""
        result  = _predict(_features())
        expected = max(result['confidence_valid'],
                       result['confidence_invalid'],
                       result['confidence_manual'])
        assert abs(result['top_confidence'] - expected) < 0.1

    @skip_if_no_model
    def test_valid_claim_predicted_for_strong_valid_data(self):
        """FUNC-PY-08: Clear valid-claim features should predict valid_claim."""
        result = _predict(_features())
        assert result['predicted_class'] == 'valid_claim', \
            f"Expected valid_claim, got {result['predicted_class']}"

    @skip_if_no_model
    def test_invalid_claim_predicted_for_strong_invalid_data(self):
        """FUNC-PY-09: Clear invalid features should predict invalid_claim."""
        today = date.today()
        from src.preprocessing.claim_preprocessor import build_feature_dict
        raw = {
            'purchase_date':           today - timedelta(days=730),
            'fault_date':              today - timedelta(days=5),
            'submission_date':         today,
            'warranty_expiry':         today - timedelta(days=365),  # expired
            'damage_type':             'water',
            'warranty_type':           'standard',
            'product_category':        'Smartphone',
            'purchase_price':          30000,
            'has_purchase_receipt':    False,
            'has_warranty_card':       False,
            'has_product_image':       False,
            'has_fault_evidence':      False,
            'has_repair_report':       False,
            'serial_number_match':     False,
            'had_unauthorized_repair': True,
            'is_duplicate_flag':       True,
            'repair_count':            3,
            'missing_doc_count':       5,
        }
        feats = build_feature_dict(raw)
        result = _predict(feats)
        assert result['predicted_class'] == 'invalid_claim', \
            f"Expected invalid_claim, got {result['predicted_class']}"

    @skip_if_no_model
    def test_processing_time_key_present(self):
        """FUNC-PY-10: processing_time_ms key is present."""
        result = _predict(_features())
        assert 'processing_time_ms' in result

    def test_mock_prediction_when_no_model(self):
        """FUNC-PY-11: Mock prediction returned when model file missing."""
        from src.ml.predictor import _mock_prediction
        result = _mock_prediction()
        assert 'predicted_class' in result
        assert result['predicted_class'] in ('valid_claim', 'invalid_claim', 'manual_review')

    def test_mock_prediction_confidences_sum_100(self):
        """FUNC-PY-12: Mock prediction confidence scores sum to ~100."""
        from src.ml.predictor import _mock_prediction
        result = _mock_prediction()
        total = result['confidence_valid'] + result['confidence_invalid'] + result['confidence_manual']
        assert abs(total - 100.0) < 1.5


# ── Model Accuracy Tests ───────────────────────────────────────────

class TestModelAccuracy:
    """ACC-PY-01: Verify model meets SRS 85% accuracy target."""

    @skip_if_no_model
    def test_model_accuracy_on_test_csv(self):
        """ACC-PY-01: Model achieves ≥85% accuracy on test.csv."""
        import pandas as pd
        from src.preprocessing.claim_preprocessor import build_feature_dict

        test_csv = ROOT / 'data' / 'processed' / 'test.csv'
        if not test_csv.exists():
            pytest.skip("test.csv not found")

        df = pd.read_csv(test_csv)
        correct = 0
        for _, row in df.iterrows():
            feats  = build_feature_dict(dict(row))
            result = _predict(feats)
            if result['predicted_class'] == row.get('label', ''):
                correct += 1

        accuracy = correct / len(df) * 100
        assert accuracy >= 85.0, f"Model accuracy {accuracy:.2f}% below SRS 85% target"


# ── Negative / Edge Tests ──────────────────────────────────────────

class TestPythonModelNegative:
    """NEG-PY-01 to NEG-PY-03."""

    def test_empty_feature_dict_no_crash(self):
        """NEG-PY-01: Empty feature dict returns prediction (mock or real), no crash."""
        try:
            result = _predict({})
            assert 'predicted_class' in result
        except Exception as e:
            pytest.fail(f"_predict({{}}) raised: {e}")

    def test_mock_has_error_key(self):
        """NEG-PY-02: Mock prediction has 'error' key."""
        from src.ml.predictor import _mock_prediction
        result = _mock_prediction()
        assert 'error' in result

    @skip_if_no_model
    def test_model_version_key_present(self):
        """NEG-PY-03: Result contains 'model_version' key."""
        result = _predict(_features())
        assert 'model_version' in result
