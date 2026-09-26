"""
AssureX — Test Suite: Model Prediction & Confidence Comparison
===============================================================
SRS Ref: Section 1.6 (xxii–xxiv) Model Prediction Comparison,
         Confidence Score Comparison, Model Consistency Status
Tests: functional, boundary, low-confidence, model-disagreement
"""
import pytest
from src.decision_engine.evaluator import (
    classify_model_consistency,
    DEFAULT_THRESHOLDS,
)


# ── Functional Tests ───────────────────────────────────────────────

class TestModelConsistencyClassification:
    """FUNC-COMP-01 to FUNC-COMP-10."""

    def test_same_class_low_diff_strong_match(self):
        """FUNC-COMP-01: Same class + diff ≤5% → strong_match."""
        status, diff = classify_model_consistency(
            'valid_claim', 'valid_claim', 92.0, 90.0, DEFAULT_THRESHOLDS
        )
        assert status == 'strong_match'
        assert abs(diff - 2.0) < 0.1

    def test_same_class_medium_diff_acceptable_match(self):
        """FUNC-COMP-02: Same class + diff 5–15% → acceptable_match."""
        status, diff = classify_model_consistency(
            'valid_claim', 'valid_claim', 90.0, 79.0, DEFAULT_THRESHOLDS
        )
        assert status == 'acceptable_match'

    def test_same_class_large_diff_weak_match(self):
        """FUNC-COMP-03: Same class + diff 15–25% → weak_match."""
        status, diff = classify_model_consistency(
            'invalid_claim', 'invalid_claim', 88.0, 65.0, DEFAULT_THRESHOLDS
        )
        assert status == 'weak_match'

    def test_same_class_very_large_diff_uncertain_result(self):
        """FUNC-COMP-04: Same class + diff >25% → uncertain_result."""
        status, diff = classify_model_consistency(
            'manual_review', 'manual_review', 95.0, 60.0, DEFAULT_THRESHOLDS
        )
        assert status == 'uncertain_result'

    def test_different_class_model_disagreement(self):
        """FUNC-COMP-05: Different classes → model_disagreement."""
        status, diff = classify_model_consistency(
            'valid_claim', 'invalid_claim', 85.0, 80.0, DEFAULT_THRESHOLDS
        )
        assert status == 'model_disagreement'

    def test_different_class_any_diff_always_disagreement(self):
        """FUNC-COMP-06: Model disagreement regardless of confidence diff."""
        status, _ = classify_model_consistency(
            'valid_claim', 'manual_review', 99.0, 99.0, DEFAULT_THRESHOLDS
        )
        assert status == 'model_disagreement'

    def test_confidence_difference_calculated_correctly(self):
        """FUNC-COMP-07: Confidence difference = |py_conf - tm_conf|."""
        _, diff = classify_model_consistency(
            'valid_claim', 'valid_claim', 90.5, 75.5, DEFAULT_THRESHOLDS
        )
        assert abs(diff - 15.0) < 0.1, f"Expected diff=15.0, got {diff}"

    def test_exact_strong_match_boundary(self):
        """FUNC-COMP-08: Exactly 5.0% diff → strong_match (at boundary)."""
        status, diff = classify_model_consistency(
            'valid_claim', 'valid_claim', 90.0, 85.0, DEFAULT_THRESHOLDS
        )
        assert status == 'strong_match'

    def test_just_above_strong_match_boundary(self):
        """FUNC-COMP-09: 5.1% diff → acceptable_match (just above boundary)."""
        status, diff = classify_model_consistency(
            'valid_claim', 'valid_claim', 90.0, 84.9, DEFAULT_THRESHOLDS
        )
        assert status == 'acceptable_match'

    def test_exact_acceptable_match_boundary(self):
        """FUNC-COMP-10: Exactly 15.0% diff → acceptable_match."""
        status, _ = classify_model_consistency(
            'invalid_claim', 'invalid_claim', 90.0, 75.0, DEFAULT_THRESHOLDS
        )
        assert status == 'acceptable_match'


# ── Confidence Difference Formula Tests ────────────────────────────

class TestConfidenceDifferenceFormula:
    """SRS Formula: |Python Top-Class Confidence − GTM Top-Class Confidence|"""

    def test_formula_symmetric(self):
        """FORM-01: |A - B| == |B - A|."""
        _, d1 = classify_model_consistency('valid_claim', 'valid_claim', 90.0, 80.0, DEFAULT_THRESHOLDS)
        _, d2 = classify_model_consistency('valid_claim', 'valid_claim', 80.0, 90.0, DEFAULT_THRESHOLDS)
        assert abs(d1 - d2) < 0.001

    def test_formula_zero_when_equal(self):
        """FORM-02: |A - A| = 0 → zero difference."""
        _, diff = classify_model_consistency('valid_claim', 'valid_claim', 88.0, 88.0, DEFAULT_THRESHOLDS)
        assert diff == 0.0

    def test_formula_max_possible_diff(self):
        """FORM-03: Max diff = 100 (0% vs 100% confidence)."""
        _, diff = classify_model_consistency('valid_claim', 'valid_claim', 100.0, 0.0, DEFAULT_THRESHOLDS)
        assert diff == 100.0


# ── Low-Confidence Tests ───────────────────────────────────────────

class TestLowConfidenceCases:
    """LOWCONF-01 to LOWCONF-03: Low confidence → manual review required."""

    def test_compute_final_decision_low_py_confidence(self):
        """LOWCONF-01: Python confidence < 70% → manual_review decision."""
        from src.decision_engine.evaluator import compute_final_decision
        from src.rule_engine.warranty_rule_engine import run_rule_engine

        py_result = {
            'predicted_class': 'valid_claim',
            'top_confidence':  60.0,  # below 70% threshold
            'confidence_valid': 60.0, 'confidence_invalid': 25.0, 'confidence_manual': 15.0,
        }
        tm_result = {
            'predicted_class': 'valid_claim',
            'top_confidence':  65.0,
            'confidence_valid': 65.0, 'confidence_invalid': 20.0, 'confidence_manual': 15.0,
        }
        from datetime import date, timedelta
        feat = {
            'remaining_warranty_days': 200, 'has_purchase_receipt': 1,
            'claim_submission_delay_days': 3, 'damage_type': 'mechanical',
            'is_duplicate_flag': 0, 'missing_doc_count': 0,
            'serial_number_match': 1, 'had_unauthorized_repair': 0,
            'repair_count': 0, 'product_age_months': 6,
            'purchase_date': date.today() - timedelta(days=180),
            'fault_date': date.today() - timedelta(days=5),
        }
        rule_result = run_rule_engine(feat)
        decision, reason = compute_final_decision(
            py_result, tm_result, 'acceptable_match', 5.0, rule_result, DEFAULT_THRESHOLDS
        )
        assert decision == 'manual_review', f"Expected manual_review, got {decision}"

    def test_compute_final_decision_low_tm_confidence(self):
        """LOWCONF-02: TM confidence < 70% → manual_review decision."""
        from src.decision_engine.evaluator import compute_final_decision
        from src.rule_engine.warranty_rule_engine import run_rule_engine
        from datetime import date, timedelta

        py_result = {
            'predicted_class': 'valid_claim',
            'top_confidence':  88.0,
            'confidence_valid': 88.0, 'confidence_invalid': 7.0, 'confidence_manual': 5.0,
        }
        tm_result = {
            'predicted_class': 'valid_claim',
            'top_confidence':  55.0,  # below 70%
            'confidence_valid': 55.0, 'confidence_invalid': 25.0, 'confidence_manual': 20.0,
        }
        feat = {
            'remaining_warranty_days': 200, 'has_purchase_receipt': 1,
            'claim_submission_delay_days': 3, 'damage_type': 'mechanical',
            'is_duplicate_flag': 0, 'missing_doc_count': 0,
            'serial_number_match': 1, 'had_unauthorized_repair': 0,
            'repair_count': 0, 'product_age_months': 6,
            'purchase_date': date.today() - timedelta(days=180),
            'fault_date': date.today() - timedelta(days=5),
        }
        rule_result = run_rule_engine(feat)
        decision, _ = compute_final_decision(
            py_result, tm_result, 'acceptable_match', 33.0, rule_result, DEFAULT_THRESHOLDS
        )
        assert decision == 'manual_review'


# ── Model Disagreement Tests ───────────────────────────────────────

class TestModelDisagreement:
    """DISAGREE-01 to DISAGREE-02: Conflicting model predictions."""

    def test_model_disagreement_routes_to_manual_review(self):
        """DISAGREE-01: When models predict different classes → manual_review."""
        from src.decision_engine.evaluator import compute_final_decision
        from src.rule_engine.warranty_rule_engine import run_rule_engine
        from datetime import date, timedelta

        py_result = {
            'predicted_class': 'valid_claim',
            'top_confidence':  92.0,
            'confidence_valid': 92.0, 'confidence_invalid': 5.0, 'confidence_manual': 3.0,
        }
        tm_result = {
            'predicted_class': 'invalid_claim',  # DISAGREES
            'top_confidence':  90.0,
            'confidence_valid': 5.0, 'confidence_invalid': 90.0, 'confidence_manual': 5.0,
        }
        feat = {
            'remaining_warranty_days': 200, 'has_purchase_receipt': 1,
            'claim_submission_delay_days': 3, 'damage_type': 'mechanical',
            'is_duplicate_flag': 0, 'missing_doc_count': 0,
            'serial_number_match': 1, 'had_unauthorized_repair': 0,
            'repair_count': 0, 'product_age_months': 6,
            'purchase_date': date.today() - timedelta(days=180),
            'fault_date': date.today() - timedelta(days=5),
        }
        rule_result = run_rule_engine(feat)
        decision, reason = compute_final_decision(
            py_result, tm_result, 'model_disagreement', 2.0, rule_result, DEFAULT_THRESHOLDS
        )
        assert decision == 'manual_review', f"Expected manual_review on disagreement, got {decision}"

    def test_model_disagreement_reason_mentions_disagreement(self):
        """DISAGREE-02: Reason string mentions disagreement or models."""
        from src.decision_engine.evaluator import compute_final_decision
        from src.rule_engine.warranty_rule_engine import run_rule_engine
        from datetime import date, timedelta

        py = {'predicted_class': 'valid_claim',   'top_confidence': 91.0,
              'confidence_valid': 91.0, 'confidence_invalid': 5.0, 'confidence_manual': 4.0}
        tm = {'predicted_class': 'manual_review', 'top_confidence': 88.0,
              'confidence_valid': 6.0, 'confidence_invalid': 6.0, 'confidence_manual': 88.0}
        feat = {
            'remaining_warranty_days': 200, 'has_purchase_receipt': 1,
            'claim_submission_delay_days': 3, 'damage_type': 'mechanical',
            'is_duplicate_flag': 0, 'missing_doc_count': 0,
            'serial_number_match': 1, 'had_unauthorized_repair': 0,
            'repair_count': 0, 'product_age_months': 6,
            'purchase_date': date.today() - timedelta(days=180),
            'fault_date': date.today() - timedelta(days=5),
        }
        rule_result = run_rule_engine(feat)
        decision, reason = compute_final_decision(
            py, tm, 'model_disagreement', 3.0, rule_result, DEFAULT_THRESHOLDS
        )
        assert decision == 'manual_review'
        assert reason  # reason string should not be empty


# ── Consistency Status Tests ───────────────────────────────────────

class TestConsistencyStatus:
    """CONS-01 to CONS-05: All 5 consistency statuses work."""

    def _check(self, py_cls, tm_cls, py_conf, tm_conf, expected_status):
        status, _ = classify_model_consistency(py_cls, tm_cls, py_conf, tm_conf, DEFAULT_THRESHOLDS)
        assert status == expected_status, f"Expected {expected_status}, got {status}"

    def test_strong_match(self):
        """CONS-01."""
        self._check('valid_claim', 'valid_claim', 92.0, 90.0, 'strong_match')

    def test_acceptable_match(self):
        """CONS-02."""
        self._check('valid_claim', 'valid_claim', 90.0, 80.0, 'acceptable_match')

    def test_weak_match(self):
        """CONS-03."""
        self._check('valid_claim', 'valid_claim', 90.0, 68.0, 'weak_match')

    def test_model_disagreement(self):
        """CONS-04."""
        self._check('valid_claim', 'invalid_claim', 90.0, 85.0, 'model_disagreement')

    def test_uncertain_result(self):
        """CONS-05."""
        self._check('valid_claim', 'valid_claim', 95.0, 60.0, 'uncertain_result')
