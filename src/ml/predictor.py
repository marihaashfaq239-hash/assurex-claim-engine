"""
AssureX — ML Model Predictor
Runtime wrapper that loads saved model and runs inference on claim features.
Caches loaded model to avoid reloading on every request.
"""
from __future__ import annotations
import logging
import time
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

_model_cache = {}


def _get_model(model_path: str, le_path: str):
    """Lazy-load and cache the model + label encoder."""
    cache_key = str(model_path)
    if cache_key not in _model_cache:
        import joblib
        logger.info(f'Loading model from {model_path}')
        _model_cache[cache_key] = {
            'pipeline': joblib.load(model_path),
            'le':       joblib.load(le_path),
        }
    return _model_cache[cache_key]['pipeline'], _model_cache[cache_key]['le']


def run_python_ml_prediction(feature_dict: dict) -> dict:
    """
    Run the trained Python ML model on a preprocessed feature dict.

    Returns:
        {
            'predicted_class':    str,   # 'valid_claim' | 'invalid_claim' | 'manual_review'
            'confidence_valid':   float, # 0-100
            'confidence_invalid': float,
            'confidence_manual':  float,
            'top_confidence':     float,
            'processing_time_ms': int,
            'model_version':      str,
        }
    """
    from django.conf import settings
    import numpy as np
    import pandas as pd

    model_path = str(settings.ML_MODEL_PATH)
    le_path    = str(settings.ML_LABEL_ENCODER_PATH)

    if not Path(model_path).exists():
        logger.warning(f'Model file not found: {model_path}. Returning mock prediction.')
        return _mock_prediction()

    start_ms = int(time.time() * 1000)

    try:
        pipeline, le = _get_model(model_path, le_path)

        # Feature columns (must match training)
        from src.ml.train_model import ALL_FEATURES
        df = pd.DataFrame([feature_dict])
        for col in ALL_FEATURES:
            if col not in df.columns:
                df[col] = 0
        df = df[ALL_FEATURES]

        proba      = pipeline.predict_proba(df)[0]
        pred_idx   = int(np.argmax(proba))
        pred_class = le.inverse_transform([pred_idx])[0]
        classes    = le.classes_

        conf = {cls: round(float(p) * 100, 2) for cls, p in zip(classes, proba)}

        elapsed = int(time.time() * 1000) - start_ms

        return {
            'predicted_class':    pred_class,
            'confidence_valid':   conf.get('valid_claim', 0.0),
            'confidence_invalid': conf.get('invalid_claim', 0.0),
            'confidence_manual':  conf.get('manual_review', 0.0),
            'top_confidence':     round(float(max(proba)) * 100, 2),
            'processing_time_ms': elapsed,
            'model_version':      'assurex_v1',
            'error':              None,
        }
    except Exception as e:
        logger.error(f'ML prediction failed: {e}')
        result = _mock_prediction()
        result['error'] = str(e)
        return result


def _mock_prediction() -> dict:
    """Returns a balanced mock when model is not available (dev/test mode)."""
    import random
    classes = ['valid_claim', 'invalid_claim', 'manual_review']
    proba   = [random.uniform(0.2, 0.5) for _ in classes]
    total   = sum(proba)
    proba   = [p / total for p in proba]
    pred    = classes[proba.index(max(proba))]
    return {
        'predicted_class':    pred,
        'confidence_valid':   round(proba[0] * 100, 2),
        'confidence_invalid': round(proba[1] * 100, 2),
        'confidence_manual':  round(proba[2] * 100, 2),
        'top_confidence':     round(max(proba) * 100, 2),
        'processing_time_ms': 0,
        'model_version':      'mock_v0',
        'error':              'model_not_found',
    }
