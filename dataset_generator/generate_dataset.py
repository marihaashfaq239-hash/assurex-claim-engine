"""
AssureX Claim Engine — Synthetic Dataset Generator
Generates 1,500 unique warranty claim records (500 per class):
  - valid_claim
  - invalid_claim
  - manual_review

Run:
    py dataset_generator/generate_dataset.py

Output:
    data/raw/assurex_claims_full.csv       (all 1500 records)
    data/processed/train.csv               (70% = 1050)
    data/processed/validation.csv          (15% = 225)
    data/processed/test.csv                (15% = 225)
"""
from __future__ import annotations
import os
import sys
import random
import csv
import json
import hashlib
from datetime import date, timedelta
from pathlib import Path

# ── Paths ──
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR  = BASE_DIR / 'data' / 'raw'
PROC_DIR = BASE_DIR / 'data' / 'processed'
RAW_DIR.mkdir(parents=True, exist_ok=True)
PROC_DIR.mkdir(parents=True, exist_ok=True)

random.seed(42)

# ── Constants ──
PRODUCT_CATEGORIES = [
    'Air Conditioner', 'Refrigerator', 'Washing Machine', 'Television',
    'Smartphone', 'Laptop', 'Microwave', 'Generator', 'Water Heater', 'Small Appliance',
]
DAMAGE_TYPES = [
    'physical', 'electrical', 'mechanical', 'software',
    'manufacturing', 'water', 'overheating', 'battery', 'display', 'other',
]
WARRANTY_TYPES    = ['standard', 'extended', 'third_party']
REPAIR_OUTCOMES   = ['fixed', 'partial', 'failed', 'replaced', 'pending']
BRANDS = [
    'Samsung', 'LG', 'Haier', 'PEL', 'Dawlance', 'Orient', 'TCL',
    'Sony', 'Philips', 'Kenwood', 'Waves', 'Super Asia',
]


def rand_date(start_year=2018, end_year=2025) -> date:
    start = date(start_year, 1, 1)
    end   = date(end_year, 12, 31)
    return start + timedelta(days=random.randint(0, (end - start).days))


def rand_bool(prob_true=0.5) -> int:
    return 1 if random.random() < prob_true else 0


def make_claim_id(index: int) -> str:
    return f'CLM-{index:07d}'


# ─────────────────────────────────────────────────────────────────
# Scenario builders for each class
# ─────────────────────────────────────────────────────────────────

def build_valid_claim(idx: int) -> dict:
    """
    Valid claim scenario:
    - Within warranty period
    - Has receipt and warranty card
    - Authorized repair only or no prior repair
    - Serial number matches
    - Fault reported within claim period
    - No contradictions
    """
    purchase_date   = rand_date(2022, 2024)
    warranty_months = random.choice([12, 18, 24, 36])
    warranty_expiry = purchase_date + timedelta(days=30 * warranty_months)
    # Fault occurs well within warranty
    fault_date      = purchase_date + timedelta(days=random.randint(30, warranty_months * 30 - 30))
    # Submitted quickly
    submission_date = fault_date + timedelta(days=random.randint(1, 10))
    today           = date.today()

    product_age_months     = round((today - purchase_date).days / 30.44, 1)
    remaining_warranty_days = max(0, (warranty_expiry - today).days)
    days_since_fault        = max(0, (today - fault_date).days)
    claim_submission_delay  = (submission_date - fault_date).days

    repair_count       = random.choice([0, 0, 0, 1])   # mostly no prior repairs
    had_unauth_repair  = False
    missing_doc_count  = random.choice([0, 0, 0, 1])

    return {
        'claim_id':              make_claim_id(idx),
        'label':                 'valid_claim',
        'product_category':      random.choice(PRODUCT_CATEGORIES),
        'brand':                 random.choice(BRANDS),
        'damage_type':           random.choice(['electrical', 'mechanical', 'manufacturing', 'software', 'display']),
        'warranty_type':         random.choice(['standard', 'extended']),
        'purchase_date':         str(purchase_date),
        'warranty_expiry':       str(warranty_expiry),
        'fault_date':            str(fault_date),
        'submission_date':       str(submission_date),
        'purchase_price':        round(random.uniform(15000, 250000), 2),
        'product_age_months':    product_age_months,
        'remaining_warranty_days': remaining_warranty_days,
        'days_since_fault':      days_since_fault,
        'claim_submission_delay_days': claim_submission_delay,
        'has_purchase_receipt':  1,
        'has_warranty_card':     1,
        'has_product_image':     rand_bool(0.9),
        'has_fault_evidence':    rand_bool(0.85),
        'has_repair_report':     rand_bool(0.3),
        'serial_number_match':   1,
        'had_unauthorized_repair': 0,
        'is_duplicate_flag':     0,
        'repair_count':          repair_count,
        'missing_doc_count':     missing_doc_count,
    }


def build_invalid_claim(idx: int) -> dict:
    """
    Invalid claim scenario:
    - Expired warranty
    - OR physical/water damage (excluded)
    - OR missing receipt
    - OR unauthorized repair
    - OR fault before purchase date (contradiction)
    - OR serial number mismatch
    """
    scenario = random.choice([
        'expired_warranty', 'excluded_damage', 'no_receipt',
        'unauthorized_repair', 'serial_mismatch', 'date_contradiction', 'duplicate',
    ])

    purchase_date = rand_date(2019, 2022)
    today = date.today()

    if scenario == 'expired_warranty':
        warranty_months = 12
        warranty_expiry = purchase_date + timedelta(days=365)
        fault_date      = warranty_expiry + timedelta(days=random.randint(30, 365))
    elif scenario == 'date_contradiction':
        warranty_months = 24
        warranty_expiry = purchase_date + timedelta(days=730)
        fault_date      = purchase_date - timedelta(days=random.randint(10, 90))  # BEFORE purchase
    else:
        warranty_months = 12
        warranty_expiry = purchase_date + timedelta(days=365)
        fault_date      = purchase_date + timedelta(days=random.randint(60, 300))

    submission_date = fault_date + timedelta(days=random.randint(1, 30))
    product_age_months = round((today - purchase_date).days / 30.44, 1)
    remaining_warranty_days = max(0, (warranty_expiry - today).days)

    return {
        'claim_id':              make_claim_id(idx),
        'label':                 'invalid_claim',
        'product_category':      random.choice(PRODUCT_CATEGORIES),
        'brand':                 random.choice(BRANDS),
        'damage_type':           'physical' if scenario == 'excluded_damage' else random.choice(DAMAGE_TYPES),
        'warranty_type':         'standard',
        'purchase_date':         str(purchase_date),
        'warranty_expiry':       str(warranty_expiry),
        'fault_date':            str(fault_date),
        'submission_date':       str(submission_date),
        'purchase_price':        round(random.uniform(5000, 200000), 2),
        'product_age_months':    product_age_months,
        'remaining_warranty_days': remaining_warranty_days,
        'days_since_fault':      max(0, (today - fault_date).days),
        'claim_submission_delay_days': (submission_date - fault_date).days,
        'has_purchase_receipt':  0 if scenario == 'no_receipt' else rand_bool(0.7),
        'has_warranty_card':     rand_bool(0.5),
        'has_product_image':     rand_bool(0.6),
        'has_fault_evidence':    rand_bool(0.5),
        'has_repair_report':     rand_bool(0.2),
        'serial_number_match':   0 if scenario == 'serial_mismatch' else 1,
        'had_unauthorized_repair': 1 if scenario == 'unauthorized_repair' else 0,
        'is_duplicate_flag':     1 if scenario == 'duplicate' else 0,
        'repair_count':          random.randint(1, 4),
        'missing_doc_count':     random.randint(1, 3),
    }


def build_manual_review_claim(idx: int) -> dict:
    """
    Manual review scenario:
    - Borderline warranty (near expiry)
    - Low confidence indicators (some docs missing, some present)
    - Mixed signals: valid damage but unauthorized repair
    - Serial number partially matching
    - High-value claim
    - Conflicting information
    """
    scenario = random.choice([
        'near_expiry', 'mixed_docs', 'borderline_damage',
        'high_value', 'conflicting_dates', 'partial_docs',
    ])

    purchase_date = rand_date(2021, 2024)
    today         = date.today()

    warranty_months = 12
    warranty_expiry = purchase_date + timedelta(days=365)

    if scenario == 'near_expiry':
        # Fault occurs when warranty has only days left
        days_left = random.randint(1, 20)
        fault_date = warranty_expiry - timedelta(days=days_left)
    elif scenario == 'conflicting_dates':
        fault_date = purchase_date + timedelta(days=random.randint(200, 400))
    else:
        fault_date = purchase_date + timedelta(days=random.randint(100, 350))

    # Late submission (borderline claim period)
    submission_date = fault_date + timedelta(days=random.randint(10, 20))

    product_age_months = round((today - purchase_date).days / 30.44, 1)
    remaining_warranty_days = max(0, (warranty_expiry - today).days)

    return {
        'claim_id':              make_claim_id(idx),
        'label':                 'manual_review',
        'product_category':      random.choice(PRODUCT_CATEGORIES),
        'brand':                 random.choice(BRANDS),
        'damage_type':           random.choice(DAMAGE_TYPES),
        'warranty_type':         random.choice(WARRANTY_TYPES),
        'purchase_date':         str(purchase_date),
        'warranty_expiry':       str(warranty_expiry),
        'fault_date':            str(fault_date),
        'submission_date':       str(submission_date),
        'purchase_price':        round(random.uniform(50000, 500000), 2),
        'product_age_months':    product_age_months,
        'remaining_warranty_days': remaining_warranty_days,
        'days_since_fault':      max(0, (today - fault_date).days),
        'claim_submission_delay_days': (submission_date - fault_date).days,
        'has_purchase_receipt':  rand_bool(0.7),
        'has_warranty_card':     rand_bool(0.6),
        'has_product_image':     rand_bool(0.7),
        'has_fault_evidence':    rand_bool(0.65),
        'has_repair_report':     rand_bool(0.4),
        'serial_number_match':   rand_bool(0.75),
        'had_unauthorized_repair': rand_bool(0.35),
        'is_duplicate_flag':     rand_bool(0.1),
        'repair_count':          random.randint(0, 2),
        'missing_doc_count':     random.randint(0, 2),
    }


# ─────────────────────────────────────────────────────────────────
# CSV field order
# ─────────────────────────────────────────────────────────────────

FIELDNAMES = [
    'claim_id', 'label',
    'product_category', 'brand', 'damage_type', 'warranty_type',
    'purchase_date', 'warranty_expiry', 'fault_date', 'submission_date',
    'purchase_price', 'product_age_months', 'remaining_warranty_days',
    'days_since_fault', 'claim_submission_delay_days',
    'has_purchase_receipt', 'has_warranty_card', 'has_product_image',
    'has_fault_evidence', 'has_repair_report',
    'serial_number_match', 'had_unauthorized_repair', 'is_duplicate_flag',
    'repair_count', 'missing_doc_count',
]


# ─────────────────────────────────────────────────────────────────
# Main generation
# ─────────────────────────────────────────────────────────────────

def generate_dataset(n_per_class: int = 500) -> list[dict]:
    records = []
    idx = 1

    print(f'Generating {n_per_class} valid claims...')
    for i in range(n_per_class):
        records.append(build_valid_claim(idx)); idx += 1

    print(f'Generating {n_per_class} invalid claims...')
    for i in range(n_per_class):
        records.append(build_invalid_claim(idx)); idx += 1

    print(f'Generating {n_per_class} manual review claims...')
    for i in range(n_per_class):
        records.append(build_manual_review_claim(idx)); idx += 1

    # Shuffle
    random.shuffle(records)
    return records


def stratified_split(records: list, train=0.70, val=0.15, test=0.15):
    """
    Stratified split: each split has equal class proportions.
    SRS requires: 70% train / 15% val / 15% test
    """
    by_class = {}
    for r in records:
        by_class.setdefault(r['label'], []).append(r)

    train_set, val_set, test_set = [], [], []
    for label, items in by_class.items():
        random.shuffle(items)
        n = len(items)
        n_train = int(n * train)
        n_val   = int(n * val)
        train_set.extend(items[:n_train])
        val_set.extend(items[n_train:n_train + n_val])
        test_set.extend(items[n_train + n_val:])

    random.shuffle(train_set)
    random.shuffle(val_set)
    random.shuffle(test_set)
    return train_set, val_set, test_set


def write_csv(records: list, path: Path):
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(records)
    print(f'  Written: {path} ({len(records)} records)')


def write_stats(records: list, path: Path):
    from collections import Counter
    labels = Counter(r['label'] for r in records)
    stats  = {
        'total':         len(records),
        'label_counts':  dict(labels),
        'label_pct':     {k: round(v / len(records) * 100, 1) for k, v in labels.items()},
    }
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2)
    print(f'  Stats:   {path}')
    return stats


if __name__ == '__main__':
    print('=== AssureX Dataset Generator ===\n')
    records = generate_dataset(500)
    print(f'\nTotal records: {len(records)}\n')

    # Write full dataset
    write_csv(records, RAW_DIR / 'assurex_claims_full.csv')
    write_stats(records, RAW_DIR / 'dataset_stats.json')

    # Stratified split
    train, val, test = stratified_split(records)
    write_csv(train, PROC_DIR / 'train.csv')
    write_csv(val,   PROC_DIR / 'validation.csv')
    write_csv(test,  PROC_DIR / 'test.csv')

    # Mapping file (claim_id → split)
    mapping = {}
    for r in train: mapping[r['claim_id']] = 'train'
    for r in val:   mapping[r['claim_id']] = 'validation'
    for r in test:  mapping[r['claim_id']] = 'test'
    with open(PROC_DIR / 'claim_split_mapping.json', 'w') as f:
        json.dump(mapping, f, indent=2)
    print(f'  Split mapping: {PROC_DIR}/claim_split_mapping.json')

    print(f'\n  Train:      {len(train)} records')
    print(f'  Validation: {len(val)} records')
    print(f'  Test:       {len(test)} records')
    print('\n=== Dataset generation complete! ===')
