"""
AssureX — Test Suite: Dataset Integrity Tests
==============================================
SRS Ref: Section 1.2 (Steps 4, Hint) Dataset Creation Requirements
Tests: dataset size, balance, split integrity, no data leakage
"""
import pytest
import pandas as pd
from pathlib import Path

ROOT     = Path(__file__).resolve().parent.parent
PROC_DIR = ROOT / 'data' / 'processed'
RAW_DIR  = ROOT / 'data' / 'raw'

CLASSES = ['valid_claim', 'invalid_claim', 'manual_review']

skip_if_no_dataset = pytest.mark.skipif(
    not (PROC_DIR / 'train.csv').exists(),
    reason="Dataset not found — run dataset_generator/generate_dataset.py first"
)


class TestDatasetSize:
    """DS-SIZE-01 to DS-SIZE-05: SRS size requirements."""

    @skip_if_no_dataset
    def test_full_dataset_has_1500_records(self):
        """DS-SIZE-01: Full dataset has exactly 1500 records."""
        full_csv = RAW_DIR / 'assurex_claims_full.csv'
        if not full_csv.exists():
            pytest.skip("Full dataset CSV not found")
        df = pd.read_csv(full_csv)
        assert len(df) == 1500, f"Expected 1500 records, got {len(df)}"

    @skip_if_no_dataset
    def test_train_set_has_1050_records(self):
        """DS-SIZE-02: Training set = 70% = 1050 records."""
        df = pd.read_csv(PROC_DIR / 'train.csv')
        assert len(df) == 1050, f"Expected 1050 train records, got {len(df)}"

    @skip_if_no_dataset
    def test_validation_set_has_225_records(self):
        """DS-SIZE-03: Validation set = 15% = 225 records."""
        df = pd.read_csv(PROC_DIR / 'validation.csv')
        assert len(df) == 225, f"Expected 225 validation records, got {len(df)}"

    @skip_if_no_dataset
    def test_test_set_has_225_records(self):
        """DS-SIZE-04: Test set = 15% = 225 records."""
        df = pd.read_csv(PROC_DIR / 'test.csv')
        assert len(df) == 225, f"Expected 225 test records, got {len(df)}"

    @skip_if_no_dataset
    def test_split_total_equals_1500(self):
        """DS-SIZE-05: Train + Val + Test = 1500 records."""
        train = len(pd.read_csv(PROC_DIR / 'train.csv'))
        val   = len(pd.read_csv(PROC_DIR / 'validation.csv'))
        test  = len(pd.read_csv(PROC_DIR / 'test.csv'))
        assert train + val + test == 1500


class TestDatasetBalance:
    """DS-BAL-01 to DS-BAL-03: Class balance requirements."""

    @skip_if_no_dataset
    def test_full_dataset_balanced_500_each(self):
        """DS-BAL-01: Full dataset has exactly 500 records per class."""
        full_csv = RAW_DIR / 'assurex_claims_full.csv'
        if not full_csv.exists():
            pytest.skip("Full dataset CSV not found")
        df = pd.read_csv(full_csv)
        counts = df['label'].value_counts()
        for cls in CLASSES:
            assert counts.get(cls, 0) == 500, \
                f"Class {cls}: expected 500, got {counts.get(cls, 0)}"

    @skip_if_no_dataset
    def test_train_set_balanced_350_each(self):
        """DS-BAL-02: Training set has 350 records per class (1050 / 3)."""
        df = pd.read_csv(PROC_DIR / 'train.csv')
        counts = df['label'].value_counts()
        for cls in CLASSES:
            assert counts.get(cls, 0) == 350, \
                f"Train {cls}: expected 350, got {counts.get(cls, 0)}"

    @skip_if_no_dataset
    def test_test_set_balanced_75_each(self):
        """DS-BAL-03: Test set has 75 records per class (225 / 3)."""
        df = pd.read_csv(PROC_DIR / 'test.csv')
        counts = df['label'].value_counts()
        for cls in CLASSES:
            assert counts.get(cls, 0) == 75, \
                f"Test {cls}: expected 75, got {counts.get(cls, 0)}"


class TestDataLeakage:
    """DS-LEAK-01 to DS-LEAK-03: No data leakage between splits."""

    @skip_if_no_dataset
    def test_no_claim_id_overlap_train_val(self):
        """DS-LEAK-01: No Claim ID appears in both train and validation."""
        train = pd.read_csv(PROC_DIR / 'train.csv')
        val   = pd.read_csv(PROC_DIR / 'validation.csv')
        overlap = set(train['claim_id']) & set(val['claim_id'])
        assert len(overlap) == 0, f"Data leakage: {len(overlap)} IDs in train AND val"

    @skip_if_no_dataset
    def test_no_claim_id_overlap_train_test(self):
        """DS-LEAK-02: No Claim ID appears in both train and test."""
        train = pd.read_csv(PROC_DIR / 'train.csv')
        test  = pd.read_csv(PROC_DIR / 'test.csv')
        overlap = set(train['claim_id']) & set(test['claim_id'])
        assert len(overlap) == 0, f"Data leakage: {len(overlap)} IDs in train AND test"

    @skip_if_no_dataset
    def test_no_claim_id_overlap_val_test(self):
        """DS-LEAK-03: No Claim ID appears in both validation and test."""
        val  = pd.read_csv(PROC_DIR / 'validation.csv')
        test = pd.read_csv(PROC_DIR / 'test.csv')
        overlap = set(val['claim_id']) & set(test['claim_id'])
        assert len(overlap) == 0, f"Data leakage: {len(overlap)} IDs in val AND test"


class TestDatasetStructure:
    """DS-STRUCT-01 to DS-STRUCT-04: Dataset columns and quality."""

    @skip_if_no_dataset
    def test_required_columns_present(self):
        """DS-STRUCT-01: All required feature columns present."""
        df = pd.read_csv(PROC_DIR / 'train.csv')
        required = [
            'claim_id', 'label',
            'damage_type', 'warranty_type', 'product_category',
            'product_age_months', 'remaining_warranty_days', 'days_since_fault',
            'claim_submission_delay_days', 'repair_count', 'missing_doc_count',
            'purchase_price', 'has_purchase_receipt', 'has_warranty_card',
            'has_product_image', 'has_fault_evidence', 'has_repair_report',
            'serial_number_match', 'had_unauthorized_repair', 'is_duplicate_flag',
        ]
        for col in required:
            assert col in df.columns, f"Missing column: {col}"

    @skip_if_no_dataset
    def test_no_missing_values_in_train(self):
        """DS-STRUCT-02: No missing values in training set."""
        df = pd.read_csv(PROC_DIR / 'train.csv')
        missing = df.isnull().sum().sum()
        assert missing == 0, f"Training set has {missing} missing values"

    @skip_if_no_dataset
    def test_unique_claim_ids_in_each_split(self):
        """DS-STRUCT-03: Claim IDs are unique within each split."""
        for split_name in ['train', 'validation', 'test']:
            df = pd.read_csv(PROC_DIR / f'{split_name}.csv')
            assert df['claim_id'].is_unique, f"{split_name}: duplicate claim IDs found"

    @skip_if_no_dataset
    def test_label_column_has_only_valid_classes(self):
        """DS-STRUCT-04: Label column contains only the 3 valid class names."""
        for split_name in ['train', 'validation', 'test']:
            df = pd.read_csv(PROC_DIR / f'{split_name}.csv')
            invalid = set(df['label']) - set(CLASSES)
            assert len(invalid) == 0, f"{split_name}: unknown labels {invalid}"
