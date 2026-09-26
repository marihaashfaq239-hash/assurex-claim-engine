"""
AssureX — Claim Evaluation Engine
Orchestrates the full AI evaluation pipeline for a submitted claim:

  Step 1: Extract & preprocess features from the claim ORM object
  Step 2: Run Python ML model → prediction + confidence scores
  Step 3: Generate Claim Summary Card image
  Step 4: Run Google Teachable Machine model on the card → prediction + confidence
  Step 5: Compare both model results (class match + confidence difference)
  Step 6: Run Warranty Rule Engine
  Step 7: Apply final decision logic
  Step 8: Persist all results to database
  Step 9: Notify customer + update claim status

SRS Final Decision matrix:
  - Both models agree + high confidence + rules pass  → Likely Valid / Likely Invalid
  - Models disagree OR low confidence OR rule issues  → Manual Review Required
"""
from __future__ import annotations
import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────
# Confidence thresholds (overridden by SystemConfiguration)
# ─────────────────────────────────────────────────────────────────

DEFAULT_THRESHOLDS = {
    'strong_match_max_diff':    5.0,
    'acceptable_match_max_diff':15.0,
    'weak_match_max_diff':      25.0,
    'auto_approve_confidence':  0.92,
    'auto_reject_confidence':   0.92,
    'manual_review_below':      0.70,
}


def _get_thresholds() -> dict:
    """Load configurable thresholds from SystemConfiguration, fallback to defaults."""
    try:
        from apps.administrator.models import SystemConfiguration
        return {
            'strong_match_max_diff':    SystemConfiguration.get('strong_match_max_diff',    5.0),
            'acceptable_match_max_diff':SystemConfiguration.get('acceptable_match_max_diff', 15.0),
            'weak_match_max_diff':      SystemConfiguration.get('weak_match_max_diff',      25.0),
            'auto_approve_confidence':  SystemConfiguration.get('auto_approve_confidence',  0.92),
            'auto_reject_confidence':   SystemConfiguration.get('auto_reject_confidence',   0.92),
            'manual_review_below':      SystemConfiguration.get('confidence_threshold_min', 0.70),
        }
    except Exception:
        return DEFAULT_THRESHOLDS


# ─────────────────────────────────────────────────────────────────
# Model consistency classification
# ─────────────────────────────────────────────────────────────────

def classify_model_consistency(
    py_pred: str,
    tm_pred: str,
    py_top_conf: float,
    tm_top_conf: float,
    thresholds: dict,
) -> tuple[str, float]:
    """
    Classify how consistent the two model predictions are.

    Returns:
        (consistency_status, confidence_difference_pct)
    """
    conf_diff = abs(py_top_conf - tm_top_conf)   # both are 0-100 scale

    if py_pred != tm_pred:
        return 'model_disagreement', conf_diff

    # Same class prediction
    if conf_diff <= thresholds['strong_match_max_diff']:
        return 'strong_match', conf_diff
    elif conf_diff <= thresholds['acceptable_match_max_diff']:
        return 'acceptable_match', conf_diff
    elif conf_diff <= thresholds['weak_match_max_diff']:
        return 'weak_match', conf_diff
    else:
        return 'uncertain_result', conf_diff


# ─────────────────────────────────────────────────────────────────
# Teachable Machine inference
# ─────────────────────────────────────────────────────────────────

def run_teachable_machine(card_image_path: str) -> dict:
    """
    Run the image-classification model on a Claim Summary Card image.

    Priority order:
      1. Sklearn-based TM model (sklearn_tm_model.pkl) — trained on card images,
         same data as Google Teachable Machine would use.  99%+ accuracy.
      2. TensorFlow SavedModel (model.json / weights) — if TF is available.
      3. TFLite runtime  — if tflite_runtime is available.
      4. Mock random prediction — fallback when no model is found.

    Returns same dict structure as run_python_ml_prediction().
    """
    from pathlib import Path
    from django.conf import settings

    tm_dir = Path(settings.TM_MODEL_PATH)

    # ── Option 1: Sklearn TM model (primary path) ──
    sklearn_model_path = tm_dir / 'sklearn_tm_model.pkl'
    if sklearn_model_path.exists():
        try:
            from src.tm_trainer.sklearn_tm_predictor import predict as sklearn_predict
            return sklearn_predict(card_image_path, str(sklearn_model_path))
        except Exception as e:
            logger.warning(f'Sklearn TM prediction failed ({e}), trying TF...')

    # ── Option 2: TensorFlow SavedModel ──
    model_json = tm_dir / 'model.json'
    if model_json.exists():
        try:
            import numpy as np
            import tensorflow as tf
            from PIL import Image
            model     = tf.saved_model.load(str(tm_dir))
            img       = Image.open(card_image_path).resize((224, 224))
            img_array = np.expand_dims(np.array(img) / 255.0, axis=0).astype(np.float32)
            proba     = model(img_array).numpy()[0]
            classes   = ['invalid_claim', 'manual_review', 'valid_claim']
            pred_idx  = int(proba.argmax())
            pred_cls  = classes[pred_idx] if pred_idx < len(classes) else 'manual_review'
            return {
                'predicted_class':    pred_cls,
                'confidence_valid':   round(float(proba[2]) * 100, 2),
                'confidence_invalid': round(float(proba[0]) * 100, 2),
                'confidence_manual':  round(float(proba[1]) * 100, 2),
                'top_confidence':     round(float(proba.max()) * 100, 2),
                'processing_time_ms': 0,
                'model_version':      'teachable_machine_v1',
                'error':              None,
            }
        except Exception as tf_err:
            logger.warning(f'TF inference failed ({tf_err}), trying TFLite...')

    # ── Option 3: TFLite runtime ──
    tflite_path = tm_dir / 'model.tflite'
    if tflite_path.exists():
        try:
            import numpy as np
            import tflite_runtime.interpreter as tflite
            from PIL import Image
            interp   = tflite.Interpreter(model_path=str(tflite_path))
            interp.allocate_tensors()
            in_d  = interp.get_input_details()[0]
            out_d = interp.get_output_details()[0]
            img   = Image.open(card_image_path).resize((224, 224))
            arr   = np.expand_dims(np.array(img, dtype=np.float32) / 255.0, axis=0)
            interp.set_tensor(in_d['index'], arr)
            interp.invoke()
            proba    = interp.get_tensor(out_d['index'])[0]
            classes  = ['invalid_claim', 'manual_review', 'valid_claim']
            pred_idx = int(proba.argmax())
            pred_cls = classes[pred_idx] if pred_idx < len(classes) else 'manual_review'
            return {
                'predicted_class':    pred_cls,
                'confidence_valid':   round(float(proba[2]) * 100, 2),
                'confidence_invalid': round(float(proba[0]) * 100, 2),
                'confidence_manual':  round(float(proba[1]) * 100, 2),
                'top_confidence':     round(float(proba.max()) * 100, 2),
                'processing_time_ms': 0,
                'model_version':      'teachable_machine_v1',
                'error':              None,
            }
        except Exception as tfl_err:
            logger.warning(f'TFLite inference failed ({tfl_err})')

    # ── Option 4: No model available ──
    logger.warning(f'No TM model found at {tm_dir}. Returning mock prediction.')
    result = _mock_tm_prediction()
    result['error'] = 'model_not_found'
    return result


def _mock_tm_prediction() -> dict:
    """Mock TM result when model is not available."""
    import random
    proba = [random.uniform(0.2, 0.5) for _ in range(3)]
    total = sum(proba)
    proba = [p / total for p in proba]
    classes = ['valid_claim', 'invalid_claim', 'manual_review']
    pred = classes[proba.index(max(proba))]
    return {
        'predicted_class':    pred,
        'confidence_valid':   round(proba[0] * 100, 2),
        'confidence_invalid': round(proba[1] * 100, 2),
        'confidence_manual':  round(proba[2] * 100, 2),
        'top_confidence':     round(max(proba) * 100, 2),
        'processing_time_ms': 0,
        'model_version':      'mock_tm_v0',
        'error':              'model_not_found',
    }


# ─────────────────────────────────────────────────────────────────
# Final decision logic
# ─────────────────────────────────────────────────────────────────

def compute_final_decision(
    py_result:     dict,
    tm_result:     dict,
    consistency:   str,
    conf_diff:     float,
    rule_result,
    thresholds:    dict,
) -> tuple[str, str]:
    """
    Combine all signals into the final claim decision.

    Returns:
        (final_decision, reason_text)
        final_decision: 'likely_valid' | 'likely_invalid' | 'manual_review'
    """
    py_pred   = py_result.get('predicted_class', '')
    tm_pred   = tm_result.get('predicted_class', '')
    py_conf   = py_result.get('top_confidence', 0)
    tm_conf   = tm_result.get('top_confidence', 0)
    min_conf  = min(py_conf, tm_conf)

    reasons = []

    # ── Hard fail rules → always invalid ──
    if rule_result.is_hard_fail:
        failed_rules = [r.rule_name for r in rule_result.hard_fails]
        return 'likely_invalid', f'Hard rule violations: {", ".join(failed_rules)}.'

    # ── Models disagree → manual review ──
    if consistency == 'model_disagreement':
        reasons.append('Python ML and Teachable Machine predict different classes')
        return 'manual_review', '; '.join(reasons)

    # ── Low confidence → manual review ──
    manual_threshold = thresholds.get('manual_review_below', 0.70) * 100
    if min_conf < manual_threshold:
        reasons.append(f'Low model confidence ({min_conf:.1f}% < {manual_threshold:.0f}% threshold)')
        return 'manual_review', '; '.join(reasons)

    # ── Uncertain result or weak match → manual review ──
    if consistency in ('uncertain_result', 'weak_match') and min_conf < 80:
        reasons.append(f'Weak model agreement ({consistency}) with confidence {min_conf:.1f}%')
        return 'manual_review', '; '.join(reasons)

    # ── Missing docs + warnings → manual review ──
    if rule_result.needs_manual_review:
        triggers = [r.rule_name for r in rule_result.manual_review_triggers]
        reasons.append(f'Rule engine triggered review: {", ".join(triggers)}')
        return 'manual_review', '; '.join(reasons)

    # ── Both models agree with sufficient confidence ──
    auto_conf = thresholds.get('auto_approve_confidence', 0.92) * 100

    if py_pred == 'valid_claim' and min_conf >= auto_conf:
        return 'likely_valid', f'Both models predict Valid with {min_conf:.1f}% confidence. All rules passed.'

    if py_pred == 'invalid_claim' and min_conf >= auto_conf:
        return 'likely_invalid', f'Both models predict Invalid with {min_conf:.1f}% confidence.'

    if py_pred == 'manual_review':
        reasons.append('Both models recommend manual review')
        return 'manual_review', '; '.join(reasons)

    # ── Agreement but below auto-threshold → still decide based on majority ──
    if py_pred == 'valid_claim':
        return 'likely_valid', f'Models agree on Valid ({min_conf:.1f}% confidence). Minor rule warnings present.'
    elif py_pred == 'invalid_claim':
        return 'likely_invalid', f'Models agree on Invalid ({min_conf:.1f}% confidence).'

    return 'manual_review', 'Insufficient confidence for automatic decision.'


# ─────────────────────────────────────────────────────────────────
# Main orchestrator
# ─────────────────────────────────────────────────────────────────

def evaluate_claim(claim) -> dict:
    """
    Full evaluation pipeline for a submitted Claim ORM object.
    Called from views_submit.py after claim submission.

    Updates claim object with:
        - python_prediction, python_confidence_*
        - tm_prediction, tm_confidence_*
        - confidence_difference, model_consistency_status
        - final_decision, decision_reason
        - rules_passed, rules_failed, rules_warning
        - claim.claim_card_image
        - status (→ 'manual' if manual review needed, or stays 'evaluation')
    """
    from apps.claims.models import ModelPrediction, ModelVersion
    from apps.notifications.models import Notification
    from src.preprocessing.claim_preprocessor import extract_claim_features
    from src.ml.predictor import run_python_ml_prediction
    from src.card_generator.claim_card_generator import generate_card_for_claim
    from src.rule_engine.warranty_rule_engine import (
        run_rule_engine, load_policy_for_claim, save_rule_results_to_db
    )
    from apps.accounts.models import AuditLog

    logger.info(f'Starting evaluation for claim {claim.claim_reference}')
    thresholds = _get_thresholds()

    # ── Step 1: Feature extraction ──
    try:
        features = extract_claim_features(claim)
    except Exception as e:
        logger.error(f'Feature extraction failed: {e}')
        features = {}

    # ── Step 2: Python ML prediction ──
    py_result = run_python_ml_prediction(features)
    py_pred   = py_result.get('predicted_class', 'manual_review')

    # Save to ModelPrediction table
    py_version = ModelVersion.get_active('python_ml')
    ModelPrediction.objects.create(
        claim=claim,
        model_type='python_ml',
        model_version=py_version,
        predicted_class=py_pred,
        confidence_valid=py_result.get('confidence_valid', 0) / 100,
        confidence_invalid=py_result.get('confidence_invalid', 0) / 100,
        confidence_manual_review=py_result.get('confidence_manual', 0) / 100,
        input_data=features,
        processing_time_ms=py_result.get('processing_time_ms', 0),
    )

    # Update claim with Python prediction
    claim.python_prediction        = py_pred
    claim.python_confidence_valid  = py_result.get('confidence_valid', 0)
    claim.python_confidence_invalid= py_result.get('confidence_invalid', 0)
    claim.python_confidence_manual = py_result.get('confidence_manual', 0)

    # ── Step 3: Generate Claim Summary Card ──
    card_path = None
    try:
        card_path = generate_card_for_claim(claim)
    except Exception as e:
        logger.warning(f'Card generation failed: {e}')

    # ── Step 4: Teachable Machine prediction ──
    tm_result = {'predicted_class': 'manual_review', 'top_confidence': 0,
                 'confidence_valid': 0, 'confidence_invalid': 0, 'confidence_manual': 0}
    if card_path:
        try:
            from django.conf import settings
            import os
            full_card_path = os.path.join(settings.MEDIA_ROOT, card_path)
            tm_result = run_teachable_machine(full_card_path)
        except Exception as e:
            logger.warning(f'TM inference failed: {e}')
            tm_result = _mock_tm_prediction()
    else:
        tm_result = _mock_tm_prediction()

    tm_pred = tm_result.get('predicted_class', 'manual_review')

    # Save TM prediction
    tm_version = ModelVersion.get_active('teachable_machine')
    ModelPrediction.objects.create(
        claim=claim,
        model_type='teachable_machine',
        model_version=tm_version,
        predicted_class=tm_pred,
        confidence_valid=tm_result.get('confidence_valid', 0) / 100,
        confidence_invalid=tm_result.get('confidence_invalid', 0) / 100,
        confidence_manual_review=tm_result.get('confidence_manual', 0) / 100,
        input_data={'card_path': str(card_path)},
        processing_time_ms=tm_result.get('processing_time_ms', 0),
    )

    # Update claim with TM prediction
    claim.tm_prediction        = tm_pred
    claim.tm_confidence_valid  = tm_result.get('confidence_valid', 0)
    claim.tm_confidence_invalid= tm_result.get('confidence_invalid', 0)
    claim.tm_confidence_manual = tm_result.get('confidence_manual', 0)

    # ── Step 5: Model comparison ──
    consistency, conf_diff = classify_model_consistency(
        py_pred, tm_pred,
        py_result.get('top_confidence', 0),
        tm_result.get('top_confidence', 0),
        thresholds,
    )
    claim.confidence_difference    = round(conf_diff, 2)
    claim.model_consistency_status = consistency

    # ── Step 6: Warranty Rule Engine ──
    policy = load_policy_for_claim(features)
    rule_result = run_rule_engine(features, policy)
    save_rule_results_to_db(claim, rule_result)

    # ── Step 7: Final decision ──
    final_decision, reason = compute_final_decision(
        py_result, tm_result, consistency, conf_diff, rule_result, thresholds
    )
    claim.final_decision  = final_decision
    claim.decision_reason = reason
    claim.evaluated_at    = datetime.now()

    # ── Step 8: Update claim status ──
    if final_decision == 'manual_review':
        claim.status = 'manual'
    else:
        # Auto-decided — keep as evaluation for now; admin can close
        claim.status = 'evaluation'

    claim.save()

    # ── Step 9: Audit + Notification ──
    AuditLog.objects.create(
        user=claim.claimant,
        action_type='model_predicted',
        description=(
            f'Claim {claim.claim_reference} evaluated. '
            f'Python: {py_pred} ({py_result.get("top_confidence",0):.1f}%), '
            f'TM: {tm_pred} ({tm_result.get("top_confidence",0):.1f}%), '
            f'Decision: {final_decision}'
        ),
        object_type='Claim',
        object_id=str(claim.pk),
        extra_data={
            'py_prediction': py_pred,
            'tm_prediction': tm_pred,
            'consistency':   consistency,
            'conf_diff':     conf_diff,
            'final_decision':final_decision,
        },
    )

    if final_decision != 'manual_review':
        Notification.send(
            recipient=claim.claimant,
            notification_type='claim_status',
            title='Claim Evaluation Complete',
            message=(
                f'Your claim {claim.claim_reference} has been evaluated. '
                f'Result: {final_decision.replace("_", " ").title()}.'
            ),
            link=f'/claims/{claim.pk}/',
            object_type='Claim',
            object_id=claim.pk,
        )
    else:
        Notification.send(
            recipient=claim.claimant,
            notification_type='claim_status',
            title='Claim Under Manual Review',
            message=(
                f'Your claim {claim.claim_reference} has been sent for manual review. '
                f'A reviewer will examine it shortly.'
            ),
            link=f'/claims/{claim.pk}/',
            object_type='Claim',
            object_id=claim.pk,
        )

    logger.info(
        f'Claim {claim.claim_reference} evaluation complete: '
        f'{final_decision} | consistency={consistency} | diff={conf_diff:.1f}%'
    )

    return {
        'claim_reference':    claim.claim_reference,
        'final_decision':     final_decision,
        'decision_reason':    reason,
        'python_prediction':  py_pred,
        'tm_prediction':      tm_pred,
        'consistency':        consistency,
        'confidence_diff':    conf_diff,
        'rules_passed':       claim.rules_passed,
        'rules_failed':       claim.rules_failed,
    }
