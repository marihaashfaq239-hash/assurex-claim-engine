"""
AssureX — Sklearn-based Teachable Machine Predictor
Drop-in replacement for TensorFlow TM inference when TF is unavailable.
Called by src/decision_engine/evaluator.py::run_teachable_machine().
"""
from __future__ import annotations
import logging
import time
from pathlib import Path

import joblib
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)

CLASSES   = ["invalid_claim", "manual_review", "valid_claim"]
IMG_SIZE  = (64, 64)

_cache: dict = {}


def _load_model(model_path: str):
    if model_path not in _cache:
        _cache[model_path] = joblib.load(model_path)
    return _cache[model_path]


def _extract_features(img_path: str) -> np.ndarray:
    """Same feature extraction as train_teachable_machine.py."""
    img = Image.open(img_path).convert("RGB").resize(IMG_SIZE)
    arr = np.array(img, dtype=np.float32)
    feats = []
    for ch in range(3):
        hist, _ = np.histogram(arr[:, :, ch], bins=64, range=(0, 255))
        feats.extend(hist / (hist.sum() + 1e-8))
    for ch in range(3):
        feats.append(arr[:, :, ch].mean() / 255.0)
        feats.append(arr[:, :, ch].std()  / 255.0)
    gray  = img.convert("L").resize((8, 8))
    g_arr = np.array(gray, dtype=np.float32) / 255.0
    feats.extend(g_arr.flatten())
    gray_full = np.array(img.convert("L"), dtype=np.float32) / 255.0
    row_means = gray_full.mean(axis=1)
    col_means = gray_full.mean(axis=0)
    feats.extend([row_means[i::8].mean() for i in range(8)])
    feats.extend([col_means[i::8].mean() for i in range(8)])
    return np.array(feats, dtype=np.float32).reshape(1, -1)


def predict(img_path: str, model_path: str) -> dict:
    """
    Run sklearn TM model on a card image.
    Returns same dict structure as evaluator.run_teachable_machine().
    """
    t0 = int(time.time() * 1000)
    try:
        pipeline = _load_model(model_path)
        feats    = _extract_features(img_path)
        proba    = pipeline.predict_proba(feats)[0]
        classes  = pipeline.classes_

        # Map probabilities to our 3 fixed classes
        conf = {cls: 0.0 for cls in CLASSES}
        for cls, p in zip(classes, proba):
            if cls in conf:
                conf[cls] = round(float(p) * 100, 2)

        pred_class = max(conf, key=conf.get)
        elapsed    = int(time.time() * 1000) - t0

        return {
            "predicted_class":    pred_class,
            "confidence_valid":   conf.get("valid_claim",   0.0),
            "confidence_invalid": conf.get("invalid_claim", 0.0),
            "confidence_manual":  conf.get("manual_review", 0.0),
            "top_confidence":     conf[pred_class],
            "processing_time_ms": elapsed,
            "model_version":      "teachable_machine_v1",
            "error":              None,
        }
    except Exception as e:
        logger.error(f"Sklearn TM prediction failed: {e}")
        return {
            "predicted_class":    "manual_review",
            "confidence_valid":   33.33,
            "confidence_invalid": 33.33,
            "confidence_manual":  33.34,
            "top_confidence":     33.34,
            "processing_time_ms": 0,
            "model_version":      "teachable_machine_v1",
            "error":              str(e),
        }
