"""
AssureX — Test Suite: Integration Tests
========================================
SRS Ref: Section 1.2 (Full pipeline Steps 1–12)
Tests: end-to-end pipeline integration, component interoperability
"""
import pytest
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _raw_claim(overrides=None):
    today = date.today()
    base = {
        'purchase_date':                today - timedelta(days=180),
        'fault_date':                   today - timedelta(days=5),
        'submission_date':              today,
        'warranty_expiry':              today + timedelta(days=185),
        'damage_type':                  'mechanical',
        'warranty_type':                'standard',
        'product_category':             'Washing Machine',
        'brand':                        'Samsung',
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
    return base


class TestPreprocessingToRuleEngine:
    """INT-01: Preprocessor output flows correctly into rule engine."""

    def test_preprocessor_output_accepted_by_rule_engine(self):
        """INT-01: Features from build_feature_dict() can be passed to run_rule_engine()."""
        from src.preprocessing.claim_preprocessor import build_feature_dict
        from src.rule_engine.warranty_rule_engine import run_rule_engine

        features = build_feature_dict(_raw_claim())
        result = run_rule_engine(features)
        assert result is not None
        assert hasattr(result, 'passed')
        assert hasattr(result, 'failed')

    def test_valid_raw_claim_passes_rules(self):
        """INT-02: Valid raw claim → valid features → rules all pass."""
        from src.preprocessing.claim_preprocessor import build_feature_dict
        from src.rule_engine.warranty_rule_engine import run_rule_engine

        features = build_feature_dict(_raw_claim())
        result = run_rule_engine(features)
        assert not result.is_hard_fail        # @property
        assert not result.needs_manual_review  # @property

    def test_invalid_raw_claim_fails_rules(self):
        """INT-03: Invalid raw claim → features → rule fails."""
        from src.preprocessing.claim_preprocessor import build_feature_dict
        from src.rule_engine.warranty_rule_engine import run_rule_engine

        today = date.today()
        invalid = _raw_claim({
            'warranty_expiry':     today - timedelta(days=365),  # expired
            'has_purchase_receipt': False,
        })
        features = build_feature_dict(invalid)
        result = run_rule_engine(features)
        assert result.is_hard_fail   # @property


class TestPreprocessingToPythonModel:
    """INT-04 to INT-05: Preprocessor → Python ML model."""

    def test_features_fed_to_ml_model_no_crash(self):
        """INT-04: Features from preprocessor accepted by Python ML predictor."""
        from src.preprocessing.claim_preprocessor import build_feature_dict
        from src.ml.predictor import run_python_ml_prediction

        features = build_feature_dict(_raw_claim())
        result = run_python_ml_prediction(features)
        assert 'predicted_class' in result

    def test_ml_result_has_three_confidence_values(self):
        """INT-05: ML model produces exactly 3 confidence values."""
        from src.preprocessing.claim_preprocessor import build_feature_dict
        from src.ml.predictor import run_python_ml_prediction

        features = build_feature_dict(_raw_claim())
        result = run_python_ml_prediction(features)
        assert 'confidence_valid'   in result
        assert 'confidence_invalid' in result
        assert 'confidence_manual'  in result


class TestCardGeneratorToTMModel:
    """INT-06 to INT-07: Card generator → TM model."""

    def test_card_bytes_valid_for_tm_predictor(self, tmp_path):
        """INT-06: Card bytes from generator can be saved and used by TM predictor."""
        from src.card_generator.claim_card_generator import generate_claim_card
        from src.tm_trainer.sklearn_tm_predictor import predict

        card_data = {
            'claim_id': 'CLM-INT-TEST',
            'product_category': 'Washing Machine', 'brand': 'LG',
            'damage_type': 'mechanical', 'warranty_type': 'standard',
            'product_age_months': 12.0, 'remaining_warranty_days': 180,
            'days_since_fault': 5, 'claim_submission_delay_days': 5,
            'purchase_price': 45000,
            'has_purchase_receipt': 1, 'has_warranty_card': 1,
            'has_product_image': 1, 'has_fault_evidence': 1,
            'has_repair_report': 0, 'serial_number_match': 1,
            'had_unauthorized_repair': 0, 'is_duplicate_flag': 0,
            'repair_count': 0, 'missing_doc_count': 0,
        }
        card_bytes = generate_claim_card(card_data, variation=0)
        assert card_bytes is not None

        card_path = tmp_path / 'int_test_card.png'
        card_path.write_bytes(card_bytes)

        tm_model = ROOT / 'model' / 'teachable_machine' / 'sklearn_tm_model.pkl'
        if not tm_model.exists():
            pytest.skip("TM model not available")

        result = predict(str(card_path), str(tm_model))
        assert 'predicted_class' in result
        assert result['predicted_class'] in ('valid_claim', 'invalid_claim', 'manual_review')

    def test_invalid_card_produces_prediction(self, tmp_path):
        """INT-07: Invalid-claim card produces a prediction (any class)."""
        from src.card_generator.claim_card_generator import generate_claim_card
        from src.tm_trainer.sklearn_tm_predictor import predict

        tm_model = ROOT / 'model' / 'teachable_machine' / 'sklearn_tm_model.pkl'
        if not tm_model.exists():
            pytest.skip("TM model not available")

        invalid_data = {
            'claim_id': 'CLM-I', 'product_category': 'Smartphone', 'brand': 'Samsung',
            'damage_type': 'water', 'warranty_type': 'standard',
            'product_age_months': 36.0, 'remaining_warranty_days': 0,
            'days_since_fault': 30, 'claim_submission_delay_days': 30,
            'purchase_price': 30000,
            'has_purchase_receipt': 0, 'has_warranty_card': 0,
            'has_product_image': 0, 'has_fault_evidence': 0,
            'has_repair_report': 0, 'serial_number_match': 0,
            'had_unauthorized_repair': 1, 'is_duplicate_flag': 1,
            'repair_count': 4, 'missing_doc_count': 5,
        }
        card_bytes = generate_claim_card(invalid_data, variation=0)
        card_path = tmp_path / 'invalid_card.png'
        card_path.write_bytes(card_bytes)
        result = predict(str(card_path), str(tm_model))
        # Just verify it returns a valid class — exact prediction depends on model
        assert result['predicted_class'] in ('valid_claim', 'invalid_claim', 'manual_review')
        assert result['top_confidence'] > 0


class TestFullConsistencyClassification:
    """INT-08: Full consistency classification from models to final decision."""

    def test_both_models_agree_valid_produces_likely_valid(self):
        """INT-08: Both models agree on valid_claim with high confidence → likely_valid."""
        from src.decision_engine.evaluator import (
            classify_model_consistency, compute_final_decision
        )
        from src.rule_engine.warranty_rule_engine import run_rule_engine

        today = date.today()
        feat = {
            'remaining_warranty_days': 200, 'has_purchase_receipt': 1,
            'claim_submission_delay_days': 3, 'damage_type': 'mechanical',
            'is_duplicate_flag': 0, 'missing_doc_count': 0,
            'serial_number_match': 1, 'had_unauthorized_repair': 0,
            'repair_count': 0, 'product_age_months': 6,
            'purchase_date': today - timedelta(days=180),
            'fault_date': today - timedelta(days=5),
            'submission_date': today,
        }
        rule_result = run_rule_engine(feat)

        py_result = {
            'predicted_class': 'valid_claim', 'top_confidence': 93.0,
            'confidence_valid': 93.0, 'confidence_invalid': 4.0, 'confidence_manual': 3.0,
        }
        tm_result = {
            'predicted_class': 'valid_claim', 'top_confidence': 91.0,
            'confidence_valid': 91.0, 'confidence_invalid': 5.0, 'confidence_manual': 4.0,
        }

        consistency, conf_diff = classify_model_consistency(
            'valid_claim', 'valid_claim', 93.0, 91.0,
            {'strong_match_max_diff': 5.0, 'acceptable_match_max_diff': 15.0,
             'weak_match_max_diff': 25.0}
        )
        assert consistency == 'strong_match'

        decision, reason = compute_final_decision(
            py_result, tm_result, consistency, conf_diff, rule_result,
            {'auto_approve_confidence': 0.92, 'auto_reject_confidence': 0.92,
             'manual_review_below': 0.70}
        )
        assert decision == 'likely_valid', f"Expected likely_valid, got {decision}"

    def test_hard_fail_rule_overrides_model_agreement(self):
        """INT-09: Hard fail rule overrides even if both models agree."""
        from src.decision_engine.evaluator import compute_final_decision
        from src.rule_engine.warranty_rule_engine import run_rule_engine

        today = date.today()
        feat = {
            'remaining_warranty_days': 0,
            'warranty_expiry': today - timedelta(days=100),
            'has_purchase_receipt': 1,
            'claim_submission_delay_days': 3,
            'damage_type': 'mechanical',
            'is_duplicate_flag': 0, 'missing_doc_count': 0,
            'serial_number_match': 1, 'had_unauthorized_repair': 0,
            'repair_count': 0, 'product_age_months': 24,
            'purchase_date': today - timedelta(days=730),
            'fault_date': today - timedelta(days=5),
            'submission_date': today,
        }
        rule_result = run_rule_engine(feat)
        assert rule_result.is_hard_fail   # @property

        py_result = {
            'predicted_class': 'valid_claim', 'top_confidence': 95.0,
            'confidence_valid': 95.0, 'confidence_invalid': 3.0, 'confidence_manual': 2.0,
        }
        tm_result = {
            'predicted_class': 'valid_claim', 'top_confidence': 93.0,
            'confidence_valid': 93.0, 'confidence_invalid': 4.0, 'confidence_manual': 3.0,
        }
        decision, _ = compute_final_decision(
            py_result, tm_result, 'strong_match', 2.0, rule_result,
            {'auto_approve_confidence': 0.92, 'auto_reject_confidence': 0.92,
             'manual_review_below': 0.70}
        )
        assert decision == 'likely_invalid', \
            f"Hard fail rule should produce likely_invalid, got {decision}"
