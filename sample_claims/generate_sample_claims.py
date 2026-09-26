"""
AssureX — Sample Claims Generator
===================================
SRS Ref: Section 1.10 (8) Test Cases — must demonstrate at least:
  1. One valid claim
  2. One invalid claim
  3. One manual-review claim
  4. One expired-warranty claim
  5. One missing-document claim
  6. One duplicate claim
  7. One contradictory claim
  8. One serial-number mismatch
  9. One unauthorized-repair claim
 10. One tricky boundary-date claim
 11. One case where the two models disagree

Run: python sample_claims/generate_sample_claims.py
Output: sample_claims/*.json  (one file per claim type)
        sample_claims/sample_claims_index.json
"""
from __future__ import annotations
import json
from datetime import date, timedelta
from pathlib import Path

OUT_DIR = Path(__file__).resolve().parent
TODAY   = date.today()


def d(offset_days: int) -> str:
    return (TODAY + timedelta(days=offset_days)).isoformat()


# ─────────────────────────────────────────────────────────────────
# Claim builders
# ─────────────────────────────────────────────────────────────────

def valid_claim() -> dict:
    """
    SAMPLE-01: Valid Claim
    All conditions met — active warranty, receipt present,
    authorized repair, serial match, within reporting window.
    Expected decision: Likely Valid
    """
    return {
        "claim_id":                   "SAMPLE-0000001",
        "scenario":                   "Valid Claim",
        "description":                "All conditions satisfied. Active warranty, receipt present, fault reported within 5 days.",
        "expected_decision":          "Likely Valid",
        "claimant_email":             "customer01@example.com",
        "product": {
            "name":                   "Samsung Front-Load Washing Machine",
            "category":               "Washing Machine",
            "brand":                  "Samsung",
            "model_number":           "WF18T8000GW",
            "serial_number":          "SN-WM-20240115-001",
            "purchase_date":          d(-180),
            "purchase_price":         85000,
            "retailer":               "ABC Electronics",
        },
        "warranty": {
            "type":                   "standard",
            "start_date":             d(-180),
            "expiry_date":            d(185),
            "remaining_days":         185,
            "is_active":              True,
        },
        "claim": {
            "fault_date":             d(-5),
            "fault_description":      "Drum not spinning. Motor makes noise during spin cycle.",
            "damage_type":            "mechanical",
            "fault_location":         "Drum motor assembly",
        },
        "documents": {
            "has_purchase_receipt":   True,
            "has_warranty_card":      True,
            "has_product_image":      True,
            "has_fault_evidence":     True,
            "has_repair_report":      False,
            "missing_doc_count":      0,
        },
        "flags": {
            "serial_number_match":    True,
            "had_unauthorized_repair": False,
            "is_duplicate_flag":      False,
            "repair_count":           0,
            "claim_submission_delay_days": 5,
        },
        "claim_summary_card":         "SAMPLE-0000001_v0.png",
    }


def invalid_claim() -> dict:
    """
    SAMPLE-02: Invalid Claim
    Multiple hard-fail conditions: expired warranty, excluded damage (water),
    no receipt, serial mismatch, unauthorized repair.
    Expected decision: Likely Invalid
    """
    return {
        "claim_id":                   "SAMPLE-0000002",
        "scenario":                   "Invalid Claim",
        "description":                "Expired warranty + water damage (excluded) + no receipt + unauthorized repair.",
        "expected_decision":          "Likely Invalid",
        "claimant_email":             "customer02@example.com",
        "product": {
            "name":                   "Haier 32-inch Smart TV",
            "category":               "Television",
            "brand":                  "Haier",
            "model_number":           "H32D6100",
            "serial_number":          "SN-TV-20210601-099",
            "purchase_date":          d(-800),
            "purchase_price":         35000,
            "retailer":               "Metro Store",
        },
        "warranty": {
            "type":                   "standard",
            "start_date":             d(-800),
            "expiry_date":            d(-435),
            "remaining_days":         0,
            "is_active":              False,
        },
        "claim": {
            "fault_date":             d(-10),
            "fault_description":      "Screen cracked after water spill during rainstorm.",
            "damage_type":            "water",
            "fault_location":         "Display panel",
        },
        "documents": {
            "has_purchase_receipt":   False,
            "has_warranty_card":      False,
            "has_product_image":      False,
            "has_fault_evidence":     False,
            "has_repair_report":      False,
            "missing_doc_count":      5,
        },
        "flags": {
            "serial_number_match":    False,
            "had_unauthorized_repair": True,
            "is_duplicate_flag":      True,
            "repair_count":           3,
            "claim_submission_delay_days": 10,
        },
        "claim_summary_card":         "SAMPLE-0000002_v0.png",
    }


def manual_review_claim() -> dict:
    """
    SAMPLE-03: Manual Review Claim
    Borderline case: warranty expiring soon, one missing doc,
    one prior repair, mild contradiction.
    Expected decision: Manual Review Required
    """
    return {
        "claim_id":                   "SAMPLE-0000003",
        "scenario":                   "Manual Review Claim",
        "description":                "Borderline case. Warranty expiring soon, missing warranty card, serial mismatch.",
        "expected_decision":          "Manual Review Required",
        "claimant_email":             "customer03@example.com",
        "product": {
            "name":                   "LG Refrigerator Double Door",
            "category":               "Refrigerator",
            "brand":                  "LG",
            "model_number":           "GL-B257DPZY",
            "serial_number":          "SN-RF-20230810-042",
            "purchase_date":          d(-355),
            "purchase_price":         70000,
            "retailer":               "Home Mart",
        },
        "warranty": {
            "type":                   "standard",
            "start_date":             d(-355),
            "expiry_date":            d(10),
            "remaining_days":         10,
            "is_active":              True,
        },
        "claim": {
            "fault_date":             d(-8),
            "fault_description":      "Compressor noise, temperature not maintained. Cooling unreliable.",
            "damage_type":            "mechanical",
            "fault_location":         "Compressor unit",
        },
        "documents": {
            "has_purchase_receipt":   True,
            "has_warranty_card":      False,
            "has_product_image":      True,
            "has_fault_evidence":     True,
            "has_repair_report":      False,
            "missing_doc_count":      1,
        },
        "flags": {
            "serial_number_match":    False,
            "had_unauthorized_repair": False,
            "is_duplicate_flag":      False,
            "repair_count":           1,
            "claim_submission_delay_days": 8,
        },
        "claim_summary_card":         "SAMPLE-0000003_v0.png",
    }


def expired_warranty_claim() -> dict:
    """
    SAMPLE-04: Expired Warranty Claim
    Warranty expired 365 days ago. Hard fail on warranty_active rule.
    Expected decision: Likely Invalid
    """
    return {
        "claim_id":                   "SAMPLE-0000004",
        "scenario":                   "Expired Warranty Claim",
        "description":                "Warranty expired 365 days ago. warranty_active rule hard fails.",
        "expected_decision":          "Likely Invalid",
        "claimant_email":             "customer04@example.com",
        "product": {
            "name":                   "Dawlance 1.5 Ton Air Conditioner",
            "category":               "Air Conditioner",
            "brand":                  "Dawlance",
            "model_number":           "Inverter-15C",
            "serial_number":          "SN-AC-20200601-017",
            "purchase_date":          d(-730),
            "purchase_price":         95000,
            "retailer":               "Al-Fatah Electronics",
        },
        "warranty": {
            "type":                   "standard",
            "start_date":             d(-730),
            "expiry_date":            d(-365),
            "remaining_days":         0,
            "is_active":              False,
        },
        "claim": {
            "fault_date":             d(-5),
            "fault_description":      "AC not cooling. Compressor starts but shuts down after 2 minutes.",
            "damage_type":            "electrical",
            "fault_location":         "Compressor",
        },
        "documents": {
            "has_purchase_receipt":   True,
            "has_warranty_card":      True,
            "has_product_image":      True,
            "has_fault_evidence":     True,
            "has_repair_report":      False,
            "missing_doc_count":      0,
        },
        "flags": {
            "serial_number_match":    True,
            "had_unauthorized_repair": False,
            "is_duplicate_flag":      False,
            "repair_count":           0,
            "claim_submission_delay_days": 5,
        },
        "rule_triggered":             "warranty_active (hard_fail) — WARRANTY EXPIRED",
        "claim_summary_card":         "SAMPLE-0000004_v0.png",
    }


def missing_document_claim() -> dict:
    """
    SAMPLE-05: Missing Document Claim
    Receipt, warranty card, and fault evidence all missing.
    Expected decision: Likely Invalid (no receipt = hard fail)
    """
    return {
        "claim_id":                   "SAMPLE-0000005",
        "scenario":                   "Missing Document Claim",
        "description":                "Purchase receipt, warranty card, and fault evidence all missing.",
        "expected_decision":          "Likely Invalid",
        "claimant_email":             "customer05@example.com",
        "product": {
            "name":                   "PEL Microwave Oven",
            "category":               "Microwave",
            "brand":                  "PEL",
            "model_number":           "PMO-23L",
            "serial_number":          "SN-MW-20240201-055",
            "purchase_date":          d(-120),
            "purchase_price":         18000,
            "retailer":               "Best Buy",
        },
        "warranty": {
            "type":                   "standard",
            "start_date":             d(-120),
            "expiry_date":            d(245),
            "remaining_days":         245,
            "is_active":              True,
        },
        "claim": {
            "fault_date":             d(-3),
            "fault_description":      "Microwave plate stopped rotating. Turntable motor issue.",
            "damage_type":            "mechanical",
            "fault_location":         "Turntable motor",
        },
        "documents": {
            "has_purchase_receipt":   False,
            "has_warranty_card":      False,
            "has_product_image":      True,
            "has_fault_evidence":     False,
            "has_repair_report":      False,
            "missing_doc_count":      3,
        },
        "flags": {
            "serial_number_match":    True,
            "had_unauthorized_repair": False,
            "is_duplicate_flag":      False,
            "repair_count":           0,
            "claim_submission_delay_days": 3,
        },
        "missing_documents":          ["Purchase Receipt", "Warranty Card", "Fault Evidence"],
        "rule_triggered":             "purchase_proof (hard_fail) — NO PURCHASE RECEIPT",
        "claim_summary_card":         "SAMPLE-0000005_v0.png",
    }


def duplicate_claim() -> dict:
    """
    SAMPLE-06: Duplicate Claim
    Same product already has an open claim. Duplicate flag set.
    Expected decision: Manual Review Required
    """
    return {
        "claim_id":                   "SAMPLE-0000006",
        "scenario":                   "Duplicate Claim",
        "description":                "Same product already has open claim CLM-0000500. Flagged as duplicate.",
        "expected_decision":          "Manual Review Required",
        "claimant_email":             "customer06@example.com",
        "original_claim_id":          "CLM-0000500",
        "product": {
            "name":                   "Orient 40-inch LED TV",
            "category":               "Television",
            "brand":                  "Orient",
            "model_number":           "OE40FG613",
            "serial_number":          "SN-TV-20230915-088",
            "purchase_date":          d(-280),
            "purchase_price":         42000,
            "retailer":               "Anees Bahri Electronics",
        },
        "warranty": {
            "type":                   "standard",
            "start_date":             d(-280),
            "expiry_date":            d(85),
            "remaining_days":         85,
            "is_active":              True,
        },
        "claim": {
            "fault_date":             d(-4),
            "fault_description":      "Display flickering. Same issue as previous claim.",
            "damage_type":            "electrical",
            "fault_location":         "Display board",
        },
        "documents": {
            "has_purchase_receipt":   True,
            "has_warranty_card":      True,
            "has_product_image":      True,
            "has_fault_evidence":     True,
            "has_repair_report":      False,
            "missing_doc_count":      0,
        },
        "flags": {
            "serial_number_match":    True,
            "had_unauthorized_repair": False,
            "is_duplicate_flag":      True,
            "repair_count":           1,
            "claim_submission_delay_days": 4,
        },
        "duplicate_of":               "CLM-0000500",
        "rule_triggered":             "duplicate_claim (manual_review) — OPEN CLAIM EXISTS",
        "claim_summary_card":         "SAMPLE-0000006_v0.png",
    }


def contradictory_claim() -> dict:
    """
    SAMPLE-07: Contradictory Claim
    Fault date is BEFORE purchase date — impossible timeline contradiction.
    Expected decision: Likely Invalid (date_contradiction hard fail)
    """
    return {
        "claim_id":                   "SAMPLE-0000007",
        "scenario":                   "Contradictory Claim",
        "description":                "Fault date (3 years ago) is BEFORE purchase date (2 years ago). Timeline impossible.",
        "expected_decision":          "Likely Invalid",
        "claimant_email":             "customer07@example.com",
        "product": {
            "name":                   "Sony Xperia Smartphone",
            "category":               "Smartphone",
            "brand":                  "Sony",
            "model_number":           "Xperia-XZ3",
            "serial_number":          "SN-SP-20220901-133",
            "purchase_date":          d(-730),
            "purchase_price":         65000,
            "retailer":               "Mobile World",
        },
        "warranty": {
            "type":                   "standard",
            "start_date":             d(-730),
            "expiry_date":            d(-365),
            "remaining_days":         0,
            "is_active":              False,
        },
        "claim": {
            "fault_date":             d(-1095),
            "fault_description":      "Battery draining rapidly. Phone shuts down unexpectedly.",
            "damage_type":            "battery",
            "fault_location":         "Battery",
        },
        "documents": {
            "has_purchase_receipt":   True,
            "has_warranty_card":      True,
            "has_product_image":      True,
            "has_fault_evidence":     True,
            "has_repair_report":      False,
            "missing_doc_count":      0,
        },
        "flags": {
            "serial_number_match":    True,
            "had_unauthorized_repair": False,
            "is_duplicate_flag":      False,
            "repair_count":           0,
            "claim_submission_delay_days": 0,
        },
        "contradiction":              "fault_date (3 years ago) is BEFORE purchase_date (2 years ago)",
        "rule_triggered":             "date_contradiction (hard_fail) — FAULT BEFORE PURCHASE",
        "claim_summary_card":         "SAMPLE-0000007_v0.png",
    }


def serial_number_mismatch_claim() -> dict:
    """
    SAMPLE-08: Serial Number Mismatch
    Serial number on receipt does not match registered product serial.
    Expected decision: Manual Review Required
    """
    return {
        "claim_id":                   "SAMPLE-0000008",
        "scenario":                   "Serial Number Mismatch",
        "description":                "Serial on receipt (SN-LT-20240310-999) differs from registered serial (SN-LT-20240310-888).",
        "expected_decision":          "Manual Review Required",
        "claimant_email":             "customer08@example.com",
        "product": {
            "name":                   "Dell Inspiron 15 Laptop",
            "category":               "Laptop",
            "brand":                  "Dell",
            "model_number":           "Inspiron-3511",
            "serial_number":          "SN-LT-20240310-888",
            "purchase_date":          d(-90),
            "purchase_price":         120000,
            "retailer":               "TechZone",
        },
        "warranty": {
            "type":                   "standard",
            "start_date":             d(-90),
            "expiry_date":            d(275),
            "remaining_days":         275,
            "is_active":              True,
        },
        "claim": {
            "fault_date":             d(-6),
            "fault_description":      "Screen flickering. Horizontal lines appear randomly on display.",
            "damage_type":            "display",
            "fault_location":         "LCD panel",
        },
        "documents": {
            "has_purchase_receipt":   True,
            "has_warranty_card":      True,
            "has_product_image":      True,
            "has_fault_evidence":     True,
            "has_repair_report":      False,
            "missing_doc_count":      0,
        },
        "flags": {
            "serial_number_match":    False,
            "had_unauthorized_repair": False,
            "is_duplicate_flag":      False,
            "repair_count":           0,
            "claim_submission_delay_days": 6,
        },
        "serial_mismatch_detail": {
            "registered_serial":      "SN-LT-20240310-888",
            "receipt_serial":         "SN-LT-20240310-999",
            "mismatch":               True,
        },
        "rule_triggered":             "serial_number_match (warning) — SERIAL MISMATCH",
        "claim_summary_card":         "SAMPLE-0000008_v0.png",
    }


def unauthorized_repair_claim() -> dict:
    """
    SAMPLE-09: Unauthorized Repair Claim
    Previous repair done at non-authorized center, voiding warranty coverage.
    Expected decision: Likely Invalid (authorized_repair_only hard fail)
    """
    return {
        "claim_id":                   "SAMPLE-0000009",
        "scenario":                   "Unauthorized Repair Claim",
        "description":                "Product was repaired at local roadside shop (unauthorized). Warranty voided.",
        "expected_decision":          "Likely Invalid",
        "claimant_email":             "customer09@example.com",
        "product": {
            "name":                   "Kenwood Split AC 1 Ton",
            "category":               "Air Conditioner",
            "brand":                  "Kenwood",
            "model_number":           "KES-1240S",
            "serial_number":          "SN-AC-20230505-201",
            "purchase_date":          d(-420),
            "purchase_price":         78000,
            "retailer":               "Cool World",
        },
        "warranty": {
            "type":                   "standard",
            "start_date":             d(-420),
            "expiry_date":            d(-55),
            "remaining_days":         0,
            "is_active":              False,
        },
        "claim": {
            "fault_date":             d(-7),
            "fault_description":      "Refrigerant leaking. AC making loud noise and not cooling.",
            "damage_type":            "mechanical",
            "fault_location":         "Refrigerant lines",
        },
        "documents": {
            "has_purchase_receipt":   True,
            "has_warranty_card":      True,
            "has_product_image":      True,
            "has_fault_evidence":     True,
            "has_repair_report":      True,
            "missing_doc_count":      0,
        },
        "repair_history": [
            {
                "repair_date":        d(-120),
                "repair_center":      "Local AC Repair Shop, Block 9 Gulshan",
                "is_authorized":      False,
                "outcome":            "Partial",
                "notes":              "Gas refilled by local technician — NOT an authorized Kenwood service center",
            }
        ],
        "flags": {
            "serial_number_match":    True,
            "had_unauthorized_repair": True,
            "is_duplicate_flag":      False,
            "repair_count":           1,
            "claim_submission_delay_days": 7,
        },
        "rule_triggered":             "authorized_repair_only (hard_fail) — UNAUTHORIZED REPAIR FOUND",
        "claim_summary_card":         "SAMPLE-0000009_v0.png",
    }


def boundary_date_claim() -> dict:
    """
    SAMPLE-10: Tricky Boundary-Date Claim
    Warranty expires exactly TODAY. Fault reported 14 days ago (at exactly the limit).
    This is the most borderline case — could go either way.
    Expected decision: Manual Review Required
    """
    return {
        "claim_id":                   "SAMPLE-0000010",
        "scenario":                   "Tricky Boundary-Date Claim",
        "description":                (
            "Warranty expires EXACTLY today. "
            "Fault was reported exactly 14 days ago (at the claim-period limit). "
            "This is a boundary edge case requiring careful review."
        ),
        "expected_decision":          "Manual Review Required",
        "claimant_email":             "customer10@example.com",
        "product": {
            "name":                   "Waves 7 kg Top-Load Washing Machine",
            "category":               "Washing Machine",
            "brand":                  "Waves",
            "model_number":           "WM-S70",
            "serial_number":          "SN-WM-20230924-350",
            "purchase_date":          d(-365),
            "purchase_price":         38000,
            "retailer":               "Galaxy Electronics",
        },
        "warranty": {
            "type":                   "standard",
            "start_date":             d(-365),
            "expiry_date":            d(0),       # expires today
            "remaining_days":         0,
            "is_active":              True,        # still active at moment of submission
        },
        "claim": {
            "fault_date":             d(-14),      # exactly 14 days ago (at limit)
            "fault_description":      "Drain pump failure. Water not draining after wash cycle.",
            "damage_type":            "mechanical",
            "fault_location":         "Drain pump",
        },
        "documents": {
            "has_purchase_receipt":   True,
            "has_warranty_card":      True,
            "has_product_image":      True,
            "has_fault_evidence":     True,
            "has_repair_report":      False,
            "missing_doc_count":      0,
        },
        "flags": {
            "serial_number_match":    True,
            "had_unauthorized_repair": False,
            "is_duplicate_flag":      False,
            "repair_count":           0,
            "claim_submission_delay_days": 14,    # exactly at the boundary
        },
        "boundary_conditions": {
            "warranty_expires_today":        True,
            "report_delay_exactly_at_limit": True,
            "submission_delay_days":         14,
            "max_allowed_days":              14,
        },
        "note":                       "Borderline: submitted on last day of warranty with maximum allowed reporting delay.",
        "claim_summary_card":         "SAMPLE-0000010_v0.png",
    }


def model_disagreement_claim() -> dict:
    """
    SAMPLE-11: Model Disagreement Case
    A borderline claim where the Python model and TM model predict different classes.
    This triggers manual review regardless of confidence levels.
    Expected decision: Manual Review Required
    """
    return {
        "claim_id":                   "SAMPLE-0000011",
        "scenario":                   "Model Disagreement Case",
        "description":                (
            "Borderline features cause Python model to predict 'valid_claim' "
            "while TM image model predicts 'manual_review'. "
            "Models disagree -> routed to manual review."
        ),
        "expected_decision":          "Manual Review Required",
        "claimant_email":             "customer11@example.com",
        "product": {
            "name":                   "TCL 55-inch 4K Smart TV",
            "category":               "Television",
            "brand":                  "TCL",
            "model_number":           "55P735",
            "serial_number":          "SN-TV-20230601-077",
            "purchase_date":          d(-300),
            "purchase_price":         62000,
            "retailer":               "Carrefour",
        },
        "warranty": {
            "type":                   "extended",
            "start_date":             d(-300),
            "expiry_date":            d(65),
            "remaining_days":         65,
            "is_active":              True,
        },
        "claim": {
            "fault_date":             d(-12),
            "fault_description":      "TV randomly restarts. Software crash or hardware instability.",
            "damage_type":            "software",
            "fault_location":         "Main board / firmware",
        },
        "documents": {
            "has_purchase_receipt":   True,
            "has_warranty_card":      False,      # one doc missing — borderline
            "has_product_image":      True,
            "has_fault_evidence":     True,
            "has_repair_report":      False,
            "missing_doc_count":      1,
        },
        "flags": {
            "serial_number_match":    True,
            "had_unauthorized_repair": False,
            "is_duplicate_flag":      False,
            "repair_count":           2,           # at limit
            "claim_submission_delay_days": 12,
        },
        "model_predictions": {
            "python_model":           "valid_claim",
            "python_confidence":      74.5,
            "tm_model":               "manual_review",
            "tm_confidence":          71.2,
            "consistency_status":     "Model Disagreement",
            "confidence_difference":  3.3,
        },
        "note":                       "Both models have moderate confidence but predict different classes. Auto-routed to manual review.",
        "claim_summary_card":         "SAMPLE-0000011_v0.png",
    }


# ─────────────────────────────────────────────────────────────────
# Write all samples
# ─────────────────────────────────────────────────────────────────

SAMPLES = [
    valid_claim,
    invalid_claim,
    manual_review_claim,
    expired_warranty_claim,
    missing_document_claim,
    duplicate_claim,
    contradictory_claim,
    serial_number_mismatch_claim,
    unauthorized_repair_claim,
    boundary_date_claim,
    model_disagreement_claim,
]

if __name__ == '__main__':
    OUT_DIR.mkdir(exist_ok=True)
    index = []

    for fn in SAMPLES:
        data  = fn()
        fname = f"{data['claim_id'].lower().replace('-', '_')}.json"
        path  = OUT_DIR / fname
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        index.append({
            'file':             fname,
            'claim_id':         data['claim_id'],
            'scenario':         data['scenario'],
            'expected_decision':data['expected_decision'],
        })
        print(f"  Created: {fname}  ({data['scenario']})")

    # Write index
    idx_path = OUT_DIR / 'sample_claims_index.json'
    with open(idx_path, 'w', encoding='utf-8') as f:
        json.dump({
            'description': 'AssureX Sample Claims — one file per required claim type (SRS Section 1.10)',
            'total':       len(index),
            'claims':      index,
        }, f, indent=2, ensure_ascii=False)

    print(f"\nAll {len(SAMPLES)} sample claims created -> {OUT_DIR}")
    print(f"Index -> {idx_path}")
