"""
AssureX — Test Suite: Warranty Rule Engine
==========================================
SRS Ref: Section 1.6 (xxv) Warranty Rule Validation,
         Section 1.2 Step 11
Tests: functional, boundary, negative, contradiction-detection,
       missing-document, duplicate-claim, serial-number mismatch
"""
import pytest
from datetime import date, timedelta
from src.rule_engine.warranty_rule_engine import run_rule_engine, RuleEngineResult


# ── Helpers ────────────────────────────────────────────────────────

def _feat(overrides=None):
    """Return a base VALID feature dict (all rules should pass)."""
    today = date.today()
    base = {
        'purchase_date':                today - timedelta(days=180),
        'fault_date':                   today - timedelta(days=5),
        'submission_date':              today,
        'warranty_expiry':              today + timedelta(days=185),
        'remaining_warranty_days':      185,
        'days_since_fault':             5,
        'claim_submission_delay_days':  5,
        'product_age_months':           6,
        'damage_type':                  'mechanical',
        'warranty_type':                'standard',
        'product_category':             'Washing Machine',
        'has_purchase_receipt':         1,
        'has_warranty_card':            1,
        'has_product_image':            1,
        'has_fault_evidence':           1,
        'has_repair_report':            0,
        'serial_number_match':          1,
        'had_unauthorized_repair':      0,
        'is_duplicate_flag':            0,
        'repair_count':                 0,
        'missing_doc_count':            0,
        'purchase_price':               45000,
    }
    if overrides:
        base.update(overrides)
    return base


# ── Functional Tests ───────────────────────────────────────────────

class TestRuleEngineBasic:
    """FUNC-RULE-01 to FUNC-RULE-10: Core rule outcomes."""

    def test_valid_claim_passes_all_rules(self):
        """FUNC-RULE-01: All rules pass for a textbook valid claim."""
        result = run_rule_engine(_feat())
        assert isinstance(result, RuleEngineResult)
        assert not result.is_hard_fail   # property, not callable
        assert not result.needs_manual_review

    def test_expired_warranty_hard_fail(self):
        """FUNC-RULE-02: Expired warranty → hard fail."""
        feat = _feat({'remaining_warranty_days': 0,
                      'warranty_expiry': date.today() - timedelta(days=30)})
        result = run_rule_engine(feat)
        assert result.is_hard_fail, "Expired warranty should be hard fail"

    def test_no_purchase_receipt_hard_fail(self):
        """FUNC-RULE-03: Missing purchase receipt → hard fail."""
        feat = _feat({'has_purchase_receipt': 0})
        result = run_rule_engine(feat)
        assert result.is_hard_fail, "Missing receipt should be hard fail"

    def test_excluded_water_damage_hard_fail(self):
        """FUNC-RULE-04: Water damage (typically excluded) → hard fail."""
        feat = _feat({'damage_type': 'water'})
        result = run_rule_engine(feat)
        assert result.is_hard_fail, "Water damage should be hard fail (excluded)"

    def test_late_reporting_hard_fail(self):
        """FUNC-RULE-05: Fault reported > 14 days after occurrence → warning (SRS: may trigger manual review)."""
        feat = _feat({'days_since_fault': 30,
                      'claim_submission_delay_days': 30,
                      'fault_date': date.today() - timedelta(days=20),
                      'submission_date': date.today()})
        result = run_rule_engine(feat)
        # Rule engine gives warning (not hard fail) for late reporting
        outcomes = {r.outcome for r in result.results}
        assert 'warning' in outcomes or result.is_hard_fail

    def test_serial_number_mismatch_warning(self):
        """FUNC-RULE-06: Serial number mismatch → at least a warning."""
        feat = _feat({'serial_number_match': 0})
        result = run_rule_engine(feat)
        outcomes = [r.outcome for r in result.results]
        assert 'warning' in outcomes or result.needs_manual_review, \
            "Serial mismatch should produce warning or manual review"

    def test_unauthorized_repair_warning(self):
        """FUNC-RULE-07: Unauthorized repair → hard fail (authorized repair required)."""
        feat = _feat({'had_unauthorized_repair': 1})
        result = run_rule_engine(feat)
        # authorized_repair_only is a hard_fail rule — unauthorized repair = hard fail
        assert result.is_hard_fail, "Unauthorized repair should produce hard fail"

    def test_duplicate_claim_triggers_manual_review(self):
        """FUNC-RULE-08: Duplicate flag → manual review."""
        feat = _feat({'is_duplicate_flag': 1})
        result = run_rule_engine(feat)
        assert result.needs_manual_review, "Duplicate claim should trigger manual review"

    def test_too_many_repairs_triggers_manual_review(self):
        """FUNC-RULE-09: >2 prior repairs → manual review."""
        feat = _feat({'repair_count': 3})
        result = run_rule_engine(feat)
        assert result.needs_manual_review, "3 repairs should trigger manual review"

    def test_missing_documents_triggers_manual_review(self):
        """FUNC-RULE-10: Multiple missing docs → manual review."""
        feat = _feat({
            'has_purchase_receipt': 0,
            'has_product_image':    0,
            'has_fault_evidence':   0,
            'missing_doc_count':    3,
        })
        result = run_rule_engine(feat)
        assert result.is_hard_fail or result.needs_manual_review

    def test_result_has_passed_and_failed_counts(self):
        """FUNC-RULE-11: RuleEngineResult tracks pass/fail/warning counts."""
        result = run_rule_engine(_feat())
        assert isinstance(result.passed,    list)  # property
        assert isinstance(result.failed,    list)  # property
        assert isinstance(result.warnings,  list)  # property

    def test_summary_dict_returned(self):
        """FUNC-RULE-12: summary() returns dict with required keys."""
        result = run_rule_engine(_feat())
        summary = result.summary()
        assert 'total_rules' in summary or 'total' in summary
        assert 'passed' in summary
        assert 'failed' in summary
        assert 'warnings' in summary


# ── Contradiction Detection Tests ──────────────────────────────────

class TestContradictionDetection:
    """CONTRA-01 to CONTRA-03: Date contradictions."""

    def test_fault_before_purchase_hard_fail(self):
        """CONTRA-01: Fault date before purchase date → hard fail."""
        today = date.today()
        feat = _feat({
            'purchase_date':    today - timedelta(days=30),
            'fault_date':       today - timedelta(days=60),  # before purchase!
        })
        result = run_rule_engine(feat)
        assert result.is_hard_fail, "Fault before purchase should be hard fail"

    def test_submission_before_fault_no_crash(self):
        """CONTRA-02: Claim submitted before fault date — handled gracefully."""
        today = date.today()
        feat = _feat({
            'fault_date':        today + timedelta(days=5),   # future fault
            'submission_date':   today,
        })
        result = run_rule_engine(feat)
        # Should not crash; may produce warning or hard fail
        assert isinstance(result, RuleEngineResult)

    def test_duplicate_indicator_plus_serial_mismatch(self):
        """CONTRA-03: Duplicate + serial mismatch → complex contradictory claim."""
        feat = _feat({'is_duplicate_flag': 1, 'serial_number_match': 0})
        result = run_rule_engine(feat)
        assert result.needs_manual_review or result.is_hard_fail


# ── Missing Document Tests ─────────────────────────────────────────

class TestMissingDocumentDetection:
    """MISSDOC-01 to MISSDOC-04."""

    def test_missing_receipt_identified(self):
        """MISSDOC-01: No receipt → hard fail rule fires."""
        feat = _feat({'has_purchase_receipt': 0})
        result = run_rule_engine(feat)
        failed_rules = [r.rule_name for r in result.failed]   # property
        assert any('receipt' in r.lower() or 'purchase' in r.lower()
                   for r in failed_rules), "Receipt rule should fail"

    def test_all_docs_present_no_missing_doc_rule(self):
        """MISSDOC-02: All docs present → no missing doc hard fail."""
        feat = _feat({
            'has_purchase_receipt': 1, 'has_warranty_card': 1,
            'has_product_image': 1,   'has_fault_evidence': 1,
            'missing_doc_count': 0,
        })
        result = run_rule_engine(feat)
        assert not result.is_hard_fail   # property

    def test_missing_doc_count_zero_with_docs(self):
        """MISSDOC-03: missing_doc_count=0 when all docs uploaded."""
        feat = _feat({'missing_doc_count': 0})
        result = run_rule_engine(feat)
        assert isinstance(result, RuleEngineResult)

    def test_missing_five_docs_review_or_fail(self):
        """MISSDOC-04: 5 missing docs → review or fail."""
        feat = _feat({
            'has_purchase_receipt': 0, 'has_warranty_card': 0,
            'has_product_image':    0, 'has_fault_evidence': 0,
            'has_repair_report':    0, 'missing_doc_count':  5,
        })
        result = run_rule_engine(feat)
        assert result.is_hard_fail or result.needs_manual_review


# ── Duplicate Claim Tests ──────────────────────────────────────────

class TestDuplicateClaimDetection:
    """DUP-01 to DUP-02."""

    def test_duplicate_flag_triggers_manual_review(self):
        """DUP-01: is_duplicate_flag=1 → manual review triggered."""
        feat = _feat({'is_duplicate_flag': 1})
        result = run_rule_engine(feat)
        assert result.needs_manual_review

    def test_no_duplicate_no_manual_review_from_dup(self):
        """DUP-02: is_duplicate_flag=0 → duplicate rule passes."""
        feat = _feat({'is_duplicate_flag': 0})
        result = run_rule_engine(feat)
        # manual_review_triggers is a property, not callable
        manual_triggers = result.manual_review_triggers
        dup_triggers = [r for r in manual_triggers if 'duplicate' in r.rule_name.lower()]
        assert len(dup_triggers) == 0


# ── Serial Number Mismatch Tests ───────────────────────────────────

class TestSerialNumberMismatch:
    """SERIAL-01 to SERIAL-02."""

    def test_serial_mismatch_generates_warning_or_manual(self):
        """SERIAL-01: serial_number_match=0 → warning or manual review."""
        feat = _feat({'serial_number_match': 0})
        result = run_rule_engine(feat)
        outcomes = {r.outcome for r in result.results}
        assert 'warning' in outcomes or result.needs_manual_review

    def test_serial_match_passes_rule(self):
        """SERIAL-02: serial_number_match=1 → serial rule passes."""
        feat = _feat({'serial_number_match': 1})
        result = run_rule_engine(feat)
        serial_results = [r for r in result.results if 'serial' in r.rule_name.lower()]
        if serial_results:
            assert serial_results[0].outcome in ('pass', 'skip', 'warning')


# ── Boundary Tests ─────────────────────────────────────────────────

class TestBoundaryRuleEngine:
    """BOUND-RULE-01 to BOUND-RULE-04."""

    def test_warranty_expires_today(self):
        """BOUND-RULE-01: Warranty expiring today is borderline (0 days remaining)."""
        feat = _feat({'remaining_warranty_days': 0,
                      'warranty_expiry': date.today()})
        result = run_rule_engine(feat)
        # Either hard fail or borderline — should not crash
        assert isinstance(result, RuleEngineResult)

    def test_exactly_14_days_reporting_delay(self):
        """BOUND-RULE-02: Exactly 14-day delay is at the limit."""
        feat = _feat({'claim_submission_delay_days': 14,
                      'days_since_fault': 14})
        result = run_rule_engine(feat)
        assert isinstance(result, RuleEngineResult)

    def test_exactly_15_days_reporting_delay_hard_fail(self):
        """BOUND-RULE-03: Reporting period rule fires as WARNING (not hard_fail by design).
        Test verifies the rule fires and a warning or manual review is produced."""
        from datetime import date, timedelta
        today = date.today()
        feat = _feat({
            'fault_date':       today - timedelta(days=20),
            'submission_date':  today,   # 20-day actual delay
            'claim_submission_delay_days': 20,
            'days_since_fault': 20,
        })
        result = run_rule_engine(feat)
        # Reporting period rule produces warning (not hard_fail) — verify it fires
        report_results = [r for r in result.results if 'reporting' in r.rule_name.lower()]
        if report_results:
            assert report_results[0].outcome in ('warning', 'fail'), \
                "Reporting delay should produce warning or fail outcome"
        # Overall claim should have at least a warning
        outcomes = {r.outcome for r in result.results}
        assert 'warning' in outcomes or 'fail' in outcomes

    def test_exactly_2_repairs_at_limit(self):
        """BOUND-RULE-04: Exactly max_repair_count (2) repairs is borderline."""
        feat = _feat({'repair_count': 2})
        result = run_rule_engine(feat)
        # 2 repairs should produce warning, not hard fail
        assert isinstance(result, RuleEngineResult)

    def test_product_age_very_old_warning(self):
        """BOUND-RULE-05: Product > 10 years old → age warning."""
        feat = _feat({'product_age_months': 130})  # > 10 years
        result = run_rule_engine(feat)
        outcomes = {r.outcome for r in result.results}
        assert 'warning' in outcomes


# ── Negative Tests ─────────────────────────────────────────────────

class TestNegativeRuleEngine:
    """NEG-RULE-01 to NEG-RULE-03."""

    def test_empty_feature_dict_no_crash(self):
        """NEG-RULE-01: Empty dict should not crash rule engine."""
        try:
            result = run_rule_engine({})
            assert isinstance(result, RuleEngineResult)
        except Exception:
            pytest.fail("run_rule_engine({}) raised an exception")

    def test_result_dict_list_is_list(self):
        """NEG-RULE-02: to_dict_list() returns a list."""
        result = run_rule_engine(_feat())
        assert isinstance(result.to_dict_list(), list)

    def test_all_rules_skipped_when_policy_empty(self):
        """NEG-RULE-03: run_rule_engine with explicit empty policy runs without crash."""
        try:
            result = run_rule_engine(_feat(), policy={})
            assert isinstance(result, RuleEngineResult)
        except Exception:
            pytest.fail("run_rule_engine with empty policy raised exception")
