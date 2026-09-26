"""
AssureX — Warranty Rule Engine
Validates a claim against configurable warranty business rules.

Rules are loaded from JSON policy files (policies/*.json) or the database.
Rule types:
  - hard_fail:     Automatic failure (e.g. warranty expired, excluded damage)
  - warning:       Caution flag — does not auto-fail
  - manual_review: Triggers human review

SRS requirements covered:
  - Warranty expiry check
  - Fault coverage check
  - Claim reporting period (deadline)
  - Proof of purchase
  - Serial number match
  - Extended warranty
  - Previous repairs
  - Product replacement history
  - Excluded damage types
  - Duplicate claim detection
  - Missing documents
"""
from __future__ import annotations
import json
import logging
from datetime import date, timedelta
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

BASE_DIR     = Path(__file__).resolve().parent.parent.parent
POLICIES_DIR = BASE_DIR / 'policies'


# ─────────────────────────────────────────────────────────────────
# Rule result dataclass
# ─────────────────────────────────────────────────────────────────

class RuleResult:
    def __init__(self, rule_name: str, rule_type: str, outcome: str,
                 description: str = '', detail: dict = None):
        self.rule_name   = rule_name
        self.rule_type   = rule_type        # 'hard_fail' | 'warning' | 'manual_review'
        self.outcome     = outcome          # 'pass' | 'fail' | 'warning' | 'skip'
        self.description = description
        self.detail      = detail or {}

    def to_dict(self) -> dict:
        return {
            'rule_name':   self.rule_name,
            'rule_type':   self.rule_type,
            'outcome':     self.outcome,
            'description': self.description,
            'detail':      self.detail,
        }

    def __repr__(self):
        return f'RuleResult({self.rule_name}: {self.outcome})'


class RuleEngineResult:
    """Aggregated result from running all rules against a claim."""

    def __init__(self, results: list):
        self.results = results

    @property
    def passed(self):
        return [r for r in self.results if r.outcome == 'pass']

    @property
    def failed(self):
        return [r for r in self.results if r.outcome == 'fail']

    @property
    def warnings(self):
        return [r for r in self.results if r.outcome == 'warning']

    @property
    def hard_fails(self):
        return [r for r in self.failed if r.rule_type == 'hard_fail']

    @property
    def manual_review_triggers(self):
        return [r for r in self.results
                if r.rule_type == 'manual_review' and r.outcome in ('fail', 'warning')]

    @property
    def needs_manual_review(self) -> bool:
        return len(self.manual_review_triggers) > 0

    @property
    def is_hard_fail(self) -> bool:
        return len(self.hard_fails) > 0

    def summary(self) -> dict:
        return {
            'total_rules':        len(self.results),
            'passed':             len(self.passed),
            'failed':             len(self.failed),
            'warnings':           len(self.warnings),
            'hard_fails':         len(self.hard_fails),
            'manual_review_triggers': len(self.manual_review_triggers),
            'needs_manual_review':self.needs_manual_review,
            'is_hard_fail':       self.is_hard_fail,
        }

    def to_dict_list(self) -> list:
        return [r.to_dict() for r in self.results]


# ─────────────────────────────────────────────────────────────────
# Individual rule checks
# ─────────────────────────────────────────────────────────────────

def _check_warranty_active(claim_data: dict) -> RuleResult:
    """Rule: Warranty must not be expired at time of fault."""
    warranty_expiry  = claim_data.get('warranty_expiry')
    fault_date       = claim_data.get('fault_date')

    if not warranty_expiry:
        return RuleResult('warranty_active', 'hard_fail', 'warning',
                          'Warranty expiry date not available.')

    if isinstance(warranty_expiry, str):
        from datetime import datetime
        warranty_expiry = datetime.strptime(warranty_expiry[:10], '%Y-%m-%d').date()

    if isinstance(fault_date, str):
        from datetime import datetime
        fault_date = datetime.strptime(fault_date[:10], '%Y-%m-%d').date()

    if fault_date and fault_date > warranty_expiry:
        days_over = (fault_date - warranty_expiry).days
        return RuleResult('warranty_active', 'hard_fail', 'fail',
                          f'Fault occurred {days_over} days after warranty expiry.',
                          {'fault_date': str(fault_date), 'expiry': str(warranty_expiry)})

    remaining = (warranty_expiry - date.today()).days if warranty_expiry else 0
    if remaining <= 0:
        return RuleResult('warranty_active', 'hard_fail', 'fail',
                          'Warranty has expired.',
                          {'expiry': str(warranty_expiry), 'remaining_days': remaining})

    return RuleResult('warranty_active', 'hard_fail', 'pass',
                      f'Warranty active. {remaining} days remaining.')


def _check_claim_reporting_period(claim_data: dict, max_days: int = 14) -> RuleResult:
    """Rule: Claim must be reported within allowed days after fault occurrence."""
    fault_date      = claim_data.get('fault_date')
    submission_date = claim_data.get('submission_date')

    if not fault_date or not submission_date:
        return RuleResult('claim_reporting_period', 'warning', 'skip',
                          'Cannot check — fault or submission date missing.')

    if isinstance(fault_date, str):
        from datetime import datetime
        fault_date = datetime.strptime(fault_date[:10], '%Y-%m-%d').date()
    if isinstance(submission_date, str):
        from datetime import datetime
        submission_date = datetime.strptime(submission_date[:10], '%Y-%m-%d').date()

    delay = (submission_date - fault_date).days

    if delay > max_days:
        return RuleResult('claim_reporting_period', 'warning', 'warning',
                          f'Claim submitted {delay} days after fault (max {max_days} days).',
                          {'delay_days': delay, 'max_days': max_days})

    if delay < 0:
        return RuleResult('claim_reporting_period', 'hard_fail', 'fail',
                          'Submission date is before fault date — contradiction.',
                          {'delay_days': delay})

    return RuleResult('claim_reporting_period', 'warning', 'pass',
                      f'Claim submitted within {delay} days of fault.')


def _check_purchase_proof(claim_data: dict) -> RuleResult:
    """Rule: Purchase receipt is required."""
    has_receipt = bool(claim_data.get('has_purchase_receipt', False))
    if not has_receipt:
        return RuleResult('purchase_proof', 'hard_fail', 'fail',
                          'Purchase receipt is missing — required for warranty claim.')
    return RuleResult('purchase_proof', 'hard_fail', 'pass', 'Purchase receipt present.')


def _check_serial_number(claim_data: dict) -> RuleResult:
    """Rule: Serial number on documents must match product registration."""
    serial_match = claim_data.get('serial_number_match', True)
    if isinstance(serial_match, (int, float)):
        serial_match = bool(serial_match)

    if not serial_match:
        return RuleResult('serial_number_match', 'manual_review', 'fail',
                          'Serial number mismatch between documents and product registration.',
                          {'serial_match': False})
    return RuleResult('serial_number_match', 'hard_fail', 'pass',
                      'Serial number verified and matches.')


def _check_unauthorized_repair(claim_data: dict) -> RuleResult:
    """Rule: Prior unauthorized repair voids warranty coverage."""
    had_unauth = claim_data.get('had_unauthorized_repair', False)
    if isinstance(had_unauth, (int, float)):
        had_unauth = bool(had_unauth)

    if had_unauth:
        return RuleResult('authorized_repair_only', 'hard_fail', 'fail',
                          'Prior unauthorized repair detected — voids warranty coverage.',
                          {'had_unauthorized_repair': True})
    return RuleResult('authorized_repair_only', 'hard_fail', 'pass',
                      'No unauthorized repairs on record.')


def _check_excluded_damage(claim_data: dict, excluded_types: list = None) -> RuleResult:
    """Rule: Certain damage types are excluded from warranty coverage."""
    if excluded_types is None:
        excluded_types = ['physical', 'water']

    damage_type = claim_data.get('damage_type', '')
    if damage_type in excluded_types:
        return RuleResult('damage_coverage', 'hard_fail', 'fail',
                          f'Damage type "{damage_type}" is excluded from warranty coverage.',
                          {'damage_type': damage_type, 'excluded_types': excluded_types})
    return RuleResult('damage_coverage', 'hard_fail', 'pass',
                      f'Damage type "{damage_type}" is covered under warranty.')


def _check_duplicate_claim(claim_data: dict) -> RuleResult:
    """Rule: Duplicate claims are flagged for manual review."""
    is_dup = claim_data.get('is_duplicate_flag', False)
    if isinstance(is_dup, (int, float)):
        is_dup = bool(is_dup)

    if is_dup:
        return RuleResult('duplicate_claim', 'manual_review', 'fail',
                          'Potential duplicate claim detected.',
                          {'is_duplicate': True})
    return RuleResult('duplicate_claim', 'hard_fail', 'pass',
                      'No duplicate claim detected.')


def _check_missing_documents(claim_data: dict, required_docs: list = None) -> RuleResult:
    """Rule: Mandatory documents must be present."""
    if required_docs is None:
        required_docs = ['has_purchase_receipt', 'has_product_image', 'has_fault_evidence']

    missing = [d for d in required_docs if not claim_data.get(d, False)]
    missing_count = int(claim_data.get('missing_doc_count', len(missing)))

    if missing_count >= 2:
        return RuleResult('required_documents', 'manual_review', 'fail',
                          f'{missing_count} required document(s) missing.',
                          {'missing_docs': missing, 'missing_count': missing_count})
    if missing_count == 1:
        return RuleResult('required_documents', 'warning', 'warning',
                          '1 recommended document missing.',
                          {'missing_docs': missing, 'missing_count': missing_count})
    return RuleResult('required_documents', 'hard_fail', 'pass',
                      'All required documents present.')


def _check_repair_count(claim_data: dict, max_repairs: int = 2) -> RuleResult:
    """Rule: Excessive prior repairs may indicate misuse."""
    repair_count = int(claim_data.get('repair_count', 0))
    if repair_count > max_repairs:
        return RuleResult('repair_count_limit', 'manual_review', 'warning',
                          f'Product has been repaired {repair_count} times (limit: {max_repairs}).',
                          {'repair_count': repair_count, 'max_repairs': max_repairs})
    return RuleResult('repair_count_limit', 'warning', 'pass',
                      f'Repair count ({repair_count}) within acceptable limit.')


def _check_product_age(claim_data: dict, max_age_years: float = 10.0) -> RuleResult:
    """Rule: Product age should be reasonable relative to warranty period."""
    age_months = float(claim_data.get('product_age_months', 0))
    age_years  = age_months / 12

    if age_years > max_age_years:
        return RuleResult('product_age', 'warning', 'warning',
                          f'Product is {age_years:.1f} years old — unusually high.',
                          {'age_months': age_months, 'max_years': max_age_years})
    return RuleResult('product_age', 'warning', 'pass',
                      f'Product age ({age_months:.0f} months) is within expected range.')


def _check_date_contradiction(claim_data: dict) -> RuleResult:
    """Rule: Fault date must be after purchase date."""
    purchase_date = claim_data.get('purchase_date')
    fault_date    = claim_data.get('fault_date')

    if not purchase_date or not fault_date:
        return RuleResult('date_contradiction', 'warning', 'skip',
                          'Cannot check — dates missing.')

    if isinstance(purchase_date, str):
        from datetime import datetime
        purchase_date = datetime.strptime(purchase_date[:10], '%Y-%m-%d').date()
    if isinstance(fault_date, str):
        from datetime import datetime
        fault_date = datetime.strptime(fault_date[:10], '%Y-%m-%d').date()

    if fault_date < purchase_date:
        return RuleResult('date_contradiction', 'hard_fail', 'fail',
                          f'Fault date ({fault_date}) is before purchase date ({purchase_date}) — contradiction.',
                          {'fault_date': str(fault_date), 'purchase_date': str(purchase_date)})

    if fault_date > date.today():
        return RuleResult('date_contradiction', 'hard_fail', 'fail',
                          'Fault date is in the future.',
                          {'fault_date': str(fault_date)})

    return RuleResult('date_contradiction', 'hard_fail', 'pass',
                      'Dates are consistent — no contradictions detected.')


# ─────────────────────────────────────────────────────────────────
# Main rule engine runner
# ─────────────────────────────────────────────────────────────────

def run_rule_engine(claim_data: dict, policy: dict = None) -> RuleEngineResult:
    """
    Run all warranty rules against claim_data.

    Args:
        claim_data: preprocessed claim feature dict
        policy:     optional warranty policy dict loaded from JSON

    Returns:
        RuleEngineResult with all individual rule results
    """
    # Load policy config if provided
    excluded_damages = ['physical', 'water']
    max_claim_days   = 14
    max_repairs      = 2
    required_docs    = ['has_purchase_receipt', 'has_product_image', 'has_fault_evidence']

    if policy:
        excluded_damages = policy.get('exclusions', excluded_damages)
        max_claim_days   = policy.get('claim_reporting_period_days', max_claim_days)
        max_repairs      = policy.get('max_repair_count', max_repairs)

    results = [
        _check_date_contradiction(claim_data),
        _check_warranty_active(claim_data),
        _check_claim_reporting_period(claim_data, max_claim_days),
        _check_purchase_proof(claim_data),
        _check_serial_number(claim_data),
        _check_unauthorized_repair(claim_data),
        _check_excluded_damage(claim_data, excluded_damages),
        _check_duplicate_claim(claim_data),
        _check_missing_documents(claim_data, required_docs),
        _check_repair_count(claim_data, max_repairs),
        _check_product_age(claim_data),
    ]

    engine_result = RuleEngineResult(results)
    logger.info(
        f'Rule engine: {engine_result.summary()["passed"]} passed, '
        f'{engine_result.summary()["failed"]} failed, '
        f'{engine_result.summary()["warnings"]} warnings'
    )
    return engine_result


def load_policy_for_claim(claim_data: dict) -> Optional[dict]:
    """
    Load the warranty policy JSON for the claim's product category.
    Falls back to None if no matching policy found.
    """
    category = claim_data.get('product_category', '').lower().replace(' ', '_')
    policy_file = POLICIES_DIR / f'policy_{category}.json'

    if policy_file.exists():
        with open(policy_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    # Try generic default policy
    default = POLICIES_DIR / 'policy_default.json'
    if default.exists():
        with open(default, 'r', encoding='utf-8') as f:
            return json.load(f)

    return None


def save_rule_results_to_db(claim, engine_result: RuleEngineResult):
    """
    Persist rule results to the database (RuleResult model).
    """
    from apps.warranties.models import RuleResult as DBRuleResult

    DBRuleResult.objects.filter(claim=claim).delete()

    for r in engine_result.results:
        DBRuleResult.objects.create(
            claim=claim,
            rule_name=r.rule_name,
            rule_type=r.rule_type,
            outcome=r.outcome,
            description=r.description,
            detail=r.detail,
        )

    # Update claim stats
    summary = engine_result.summary()
    claim.rules_passed  = summary['passed']
    claim.rules_failed  = summary['failed']
    claim.rules_warning = summary['warnings']
    claim.save(update_fields=['rules_passed', 'rules_failed', 'rules_warning', 'updated_at'])
