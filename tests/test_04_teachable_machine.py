"""
AssureX — Test Suite: Teachable Machine Image Classifier
=========================================================
SRS Ref: Section 1.6 (xxi) Google Teachable Machine Classification,
         Section 1.2 Steps 8–9
Tests: functional, model accuracy, negative, boundary
"""
import pytest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TM_DIR  = ROOT / 'model' / 'teachable_machine'
TM_MODEL = TM_DIR / 'sklearn_tm_model.pkl'
CARD_DIR = ROOT / 'data' / 'claim_cards'

TM_AVAILABLE = TM_MODEL.exists()
skip_if_no_tm = pytest.mark.skipif(
    not TM_AVAILABLE,
    reason="TM model not found — run src/tm_trainer/train_teachable_machine.py first"
)
CARDS_AVAILABLE = CARD_DIR.exists() and any(CARD_DIR.rglob('*.png'))
skip_if_no_cards = pytest.mark.skipif(
    not CARDS_AVAILABLE,
    reason="Card images not found — run src/card_generator/claim_card_generator.py first"
)


# ── Functional Tests ───────────────────────────────────────────────

class TestTMPredictor:
    """FUNC-TM-01 to FUNC-TM-10."""

    def test_predictor_module_imports(self):
        """FUNC-TM-01: sklearn_tm_predictor module imports without error."""
        from src.tm_trainer.sklearn_tm_predictor import predict
        assert callable(predict)

    @skip_if_no_tm
    @skip_if_no_cards
    def test_predict_returns_dict(self, sample_card_image):
        """FUNC-TM-02: predict() returns a dict."""
        from src.tm_trainer.sklearn_tm_predictor import predict
        result = predict(sample_card_image, str(TM_MODEL))
        assert isinstance(result, dict)

    @skip_if_no_tm
    @skip_if_no_cards
    def test_predict_has_required_keys(self, sample_card_image):
        """FUNC-TM-03: Result has all required keys."""
        from src.tm_trainer.sklearn_tm_predictor import predict
        result = predict(sample_card_image, str(TM_MODEL))
        for key in ['predicted_class', 'confidence_valid', 'confidence_invalid',
                    'confidence_manual', 'top_confidence', 'error']:
            assert key in result, f"Missing key: {key}"

    @skip_if_no_tm
    @skip_if_no_cards
    def test_predicted_class_valid_label(self, sample_card_image):
        """FUNC-TM-04: predicted_class is one of the 3 valid labels."""
        from src.tm_trainer.sklearn_tm_predictor import predict
        result = predict(sample_card_image, str(TM_MODEL))
        assert result['predicted_class'] in ('valid_claim', 'invalid_claim', 'manual_review')

    @skip_if_no_tm
    @skip_if_no_cards
    def test_confidence_scores_non_negative(self, sample_card_image):
        """FUNC-TM-05: All confidence scores >= 0."""
        from src.tm_trainer.sklearn_tm_predictor import predict
        result = predict(sample_card_image, str(TM_MODEL))
        assert result['confidence_valid']   >= 0
        assert result['confidence_invalid'] >= 0
        assert result['confidence_manual']  >= 0

    @skip_if_no_tm
    @skip_if_no_cards
    def test_confidence_scores_sum_to_100(self, sample_card_image):
        """FUNC-TM-06: Three confidence scores sum to ~100%."""
        from src.tm_trainer.sklearn_tm_predictor import predict
        result = predict(sample_card_image, str(TM_MODEL))
        total = result['confidence_valid'] + result['confidence_invalid'] + result['confidence_manual']
        assert abs(total - 100.0) < 1.0, f"Sum={total}, expected ~100"

    @skip_if_no_tm
    @skip_if_no_cards
    def test_correct_prediction_valid_card(self):
        """FUNC-TM-07: Valid-claim card correctly predicted as valid_claim."""
        from src.tm_trainer.sklearn_tm_predictor import predict
        card = next((CARD_DIR / 'test' / 'valid_claim').glob('*.png'), None)
        if not card:
            pytest.skip("No valid_claim test cards found")
        result = predict(str(card), str(TM_MODEL))
        assert result['predicted_class'] == 'valid_claim', \
            f"Expected valid_claim, got {result['predicted_class']} (conf={result['top_confidence']}%)"

    @skip_if_no_tm
    @skip_if_no_cards
    def test_correct_prediction_invalid_card(self):
        """FUNC-TM-08: Invalid-claim card correctly predicted as invalid_claim."""
        from src.tm_trainer.sklearn_tm_predictor import predict
        card = next((CARD_DIR / 'test' / 'invalid_claim').glob('*.png'), None)
        if not card:
            pytest.skip("No invalid_claim test cards found")
        result = predict(str(card), str(TM_MODEL))
        assert result['predicted_class'] == 'invalid_claim', \
            f"Expected invalid_claim, got {result['predicted_class']}"

    @skip_if_no_tm
    @skip_if_no_cards
    def test_correct_prediction_manual_card(self):
        """FUNC-TM-09: Manual-review card correctly predicted as manual_review."""
        from src.tm_trainer.sklearn_tm_predictor import predict
        card = next((CARD_DIR / 'test' / 'manual_review').glob('*.png'), None)
        if not card:
            pytest.skip("No manual_review test cards found")
        result = predict(str(card), str(TM_MODEL))
        assert result['predicted_class'] == 'manual_review', \
            f"Expected manual_review, got {result['predicted_class']}"

    def test_model_version_key_present(self, sample_card_image):
        """FUNC-TM-10: model_version key present in result."""
        from src.tm_trainer.sklearn_tm_predictor import predict
        if not TM_AVAILABLE:
            pytest.skip("TM model not available")
        result = predict(sample_card_image, str(TM_MODEL))
        assert 'model_version' in result


# ── Model Accuracy Tests ───────────────────────────────────────────

class TestTMModelAccuracy:
    """ACC-TM-01: Verify TM model meets SRS 85% accuracy target."""

    @skip_if_no_tm
    @skip_if_no_cards
    def test_tm_accuracy_on_test_set(self):
        """ACC-TM-01: TM model achieves ≥85% on test card images."""
        from src.tm_trainer.sklearn_tm_predictor import predict

        classes = ['valid_claim', 'invalid_claim', 'manual_review']
        correct, total = 0, 0

        for cls in classes:
            cls_dir = CARD_DIR / 'test' / cls
            if not cls_dir.exists():
                continue
            for img_path in list(cls_dir.glob('*.png'))[:25]:  # 25 per class = 75 total
                result = predict(str(img_path), str(TM_MODEL))
                if result['predicted_class'] == cls:
                    correct += 1
                total += 1

        if total == 0:
            pytest.skip("No test card images found")

        accuracy = correct / total * 100
        assert accuracy >= 85.0, f"TM accuracy {accuracy:.2f}% below SRS 85% target"


# ── Metadata Tests ─────────────────────────────────────────────────

class TestTMMetadata:
    """META-TM-01 to META-TM-04."""

    def test_labels_file_exists(self):
        """META-TM-01: labels.txt exists."""
        assert (TM_DIR / 'labels.txt').exists(), "labels.txt not found"

    def test_labels_file_has_three_classes(self):
        """META-TM-02: labels.txt has exactly 3 classes."""
        lf = TM_DIR / 'labels.txt'
        if not lf.exists():
            pytest.skip("labels.txt not found")
        labels = [l.strip() for l in lf.read_text(encoding='utf-8').splitlines() if l.strip()]
        assert len(labels) == 3, f"Expected 3 labels, found {len(labels)}: {labels}"

    def test_metadata_json_exists(self):
        """META-TM-03: metadata.json exists."""
        assert (TM_DIR / 'metadata.json').exists(), "metadata.json not found"

    def test_metadata_accuracy_above_85(self):
        """META-TM-04: metadata.json reports test accuracy ≥ 85%."""
        import json
        meta_path = TM_DIR / 'metadata.json'
        if not meta_path.exists():
            pytest.skip("metadata.json not found")
        with open(meta_path, encoding='utf-8') as f:
            meta = json.load(f)
        assert meta.get('test_accuracy', 0) >= 85.0, \
            f"TM test accuracy {meta.get('test_accuracy')}% below 85%"

    def test_training_report_exists(self):
        """META-TM-05: tm_training_report.txt exists."""
        assert (TM_DIR / 'tm_training_report.txt').exists()


# ── Card Image Dataset Tests ───────────────────────────────────────

class TestCardImageDataset:
    """CARD-01 to CARD-05: SRS card dataset requirements."""

    @skip_if_no_cards
    def test_training_set_has_2100_images(self):
        """CARD-01: Training set has ≥ 2100 images (SRS requirement)."""
        count = sum(1 for _ in (CARD_DIR / 'train').rglob('*.png'))
        assert count >= 2100, f"Found {count} training images, SRS requires ≥2100"

    @skip_if_no_cards
    def test_three_classes_exist_in_train(self):
        """CARD-02: All 3 classes exist in training split."""
        for cls in ['valid_claim', 'invalid_claim', 'manual_review']:
            cls_dir = CARD_DIR / 'train' / cls
            assert cls_dir.exists(), f"Training class dir missing: {cls}"
            count = len(list(cls_dir.glob('*.png')))
            assert count > 0, f"No training images for class: {cls}"

    @skip_if_no_cards
    def test_validation_set_has_225_images(self):
        """CARD-03: Validation set has 225 images (75 per class × 3)."""
        count = sum(1 for _ in (CARD_DIR / 'validation').rglob('*.png'))
        assert count == 225, f"Found {count} validation images, expected 225"

    @skip_if_no_cards
    def test_test_set_has_225_images(self):
        """CARD-04: Test set has 225 images (75 per class × 3)."""
        count = sum(1 for _ in (CARD_DIR / 'test').rglob('*.png'))
        assert count == 225, f"Found {count} test images, expected 225"

    @skip_if_no_cards
    def test_card_images_are_valid_png(self):
        """CARD-05: Sample card images are valid PNG files."""
        from PIL import Image
        cards = list((CARD_DIR / 'test' / 'valid_claim').glob('*.png'))[:3]
        for card in cards:
            img = Image.open(str(card))
            assert img.format == 'PNG', f"{card.name} is not PNG"


# ── Negative Tests ─────────────────────────────────────────────────

class TestTMNegative:
    """NEG-TM-01 to NEG-TM-02."""

    def test_missing_model_file_no_crash(self, sample_card_image, tmp_path):
        """NEG-TM-01: Predict with non-existent model path returns error, no crash."""
        from src.tm_trainer.sklearn_tm_predictor import predict
        result = predict(sample_card_image, str(tmp_path / 'nonexistent.pkl'))
        assert 'predicted_class' in result
        assert result.get('error') is not None

    def test_corrupt_image_no_crash(self, tmp_path):
        """NEG-TM-02: Corrupt/empty image file handled gracefully."""
        if not TM_AVAILABLE:
            pytest.skip("TM model not available")
        from src.tm_trainer.sklearn_tm_predictor import predict
        bad_img = tmp_path / 'bad.png'
        bad_img.write_bytes(b'NOT_A_PNG_FILE_GARBAGE_DATA')
        result = predict(str(bad_img), str(TM_MODEL))
        # Should return error result, not crash
        assert 'predicted_class' in result
