"""
AssureX Claim Engine — Python ML Model Training Script
Trains and compares 3 classification algorithms:
  1. Random Forest
  2. Gradient Boosting (XGBoost)
  3. Logistic Regression

SRS requirement: minimum 85% accuracy on unseen test data.

Run:
    py src/ml/train_model.py

Outputs (saved to model/python_model/):
    assurex_model.pkl         — best model
    preprocessor.pkl          — sklearn ColumnTransformer
    label_encoder.pkl         — LabelEncoder for target
    model_comparison.json     — all 3 models' metrics
    feature_importance.json   — feature importance (RF/XGB)
    training_report.txt       — human-readable report
"""
import os
import sys
import json
import joblib
import warnings
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime

warnings.filterwarnings('ignore')

# ── Paths ──
BASE_DIR   = Path(__file__).resolve().parent.parent.parent
PROC_DIR   = BASE_DIR / 'data' / 'processed'
MODEL_DIR  = BASE_DIR / 'model' / 'python_model'
MODEL_DIR.mkdir(parents=True, exist_ok=True)

# ── Add project root to path ──
sys.path.insert(0, str(BASE_DIR))

from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, confusion_matrix, classification_report
)
from sklearn.model_selection import cross_val_score, StratifiedKFold

try:
    from xgboost import XGBClassifier
    HAS_XGB = True
except ImportError:
    HAS_XGB = False
    print('XGBoost not installed — using GradientBoostingClassifier instead.')


# ─────────────────────────────────────────────────────────────────
# Feature configuration (must match claim_preprocessor.py)
# ─────────────────────────────────────────────────────────────────

CATEGORICAL_FEATURES = [
    'product_category', 'brand', 'damage_type', 'warranty_type',
]

NUMERICAL_FEATURES = [
    'product_age_months', 'remaining_warranty_days', 'days_since_fault',
    'claim_submission_delay_days', 'purchase_price', 'repair_count',
    'missing_doc_count',
]

BINARY_FEATURES = [
    'has_purchase_receipt', 'has_warranty_card', 'has_product_image',
    'has_fault_evidence', 'has_repair_report',
    'serial_number_match', 'had_unauthorized_repair', 'is_duplicate_flag',
]

ALL_FEATURES = CATEGORICAL_FEATURES + NUMERICAL_FEATURES + BINARY_FEATURES
TARGET = 'label'


# ─────────────────────────────────────────────────────────────────
# Data loading
# ─────────────────────────────────────────────────────────────────

def _clean_df(df: pd.DataFrame) -> pd.DataFrame:
    """Convert True/False strings to 1/0 in binary columns."""
    for col in BINARY_FEATURES:
        if col in df.columns:
            df[col] = df[col].map(
                lambda x: 1 if str(x).strip().lower() in ('true', '1', 'yes') else 0
            )
    for col in NUMERICAL_FEATURES:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    return df


def load_data():
    train = _clean_df(pd.read_csv(PROC_DIR / 'train.csv'))
    val   = _clean_df(pd.read_csv(PROC_DIR / 'validation.csv'))
    test  = _clean_df(pd.read_csv(PROC_DIR / 'test.csv'))
    print(f'  Train: {len(train)} | Val: {len(val)} | Test: {len(test)}')
    return train, val, test


# ─────────────────────────────────────────────────────────────────
# Preprocessing pipeline
# ─────────────────────────────────────────────────────────────────

def build_preprocessor():
    cat_pipeline = Pipeline([
        ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))    ])
    num_pipeline = Pipeline([
        ('scaler', StandardScaler())
    ])
    preprocessor = ColumnTransformer(transformers=[
        ('cat', cat_pipeline, CATEGORICAL_FEATURES),
        ('num', num_pipeline, NUMERICAL_FEATURES),
        ('bin', 'passthrough',  BINARY_FEATURES),
    ], remainder='drop')
    return preprocessor


# ─────────────────────────────────────────────────────────────────
# Model definitions
# ─────────────────────────────────────────────────────────────────

def get_models():
    models = {
        'Random Forest': RandomForestClassifier(
            n_estimators=200,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            class_weight='balanced',
            random_state=42,
            n_jobs=-1,
        ),
        'Logistic Regression': LogisticRegression(
            C=1.0,
            max_iter=1000,
            class_weight='balanced',
            random_state=42,
            solver='lbfgs',
        ),
    }
    if HAS_XGB:
        models['XGBoost'] = XGBClassifier(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.1,
            use_label_encoder=False,
            eval_metric='mlogloss',
            random_state=42,
            n_jobs=-1,
        )
    else:
        models['Gradient Boosting'] = GradientBoostingClassifier(
            n_estimators=150,
            max_depth=5,
            learning_rate=0.1,
            random_state=42,
        )
    return models


# ─────────────────────────────────────────────────────────────────
# Training & Evaluation
# ─────────────────────────────────────────────────────────────────

def evaluate_model(name, pipeline, X_test, y_test, le):
    y_pred      = pipeline.predict(X_test)
    y_pred_proba= pipeline.predict_proba(X_test)

    accuracy  = round(accuracy_score(y_test, y_pred) * 100, 2)
    precision = round(precision_score(y_test, y_pred, average='weighted') * 100, 2)
    recall    = round(recall_score(y_test, y_pred, average='weighted') * 100, 2)
    f1        = round(f1_score(y_test, y_pred, average='weighted') * 100, 2)
    cm        = confusion_matrix(y_test, y_pred).tolist()
    cr        = classification_report(y_test, y_pred, target_names=le.classes_, output_dict=True)

    print(f'\n  {name}:')
    print(f'    Accuracy:  {accuracy}%')
    print(f'    Precision: {precision}%')
    print(f'    Recall:    {recall}%')
    print(f'    F1-Score:  {f1}%')
    if accuracy < 85:
        print(f'    ⚠ Below 85% target!')
    else:
        print(f'    ✓ Meets 85% accuracy target')

    return {
        'accuracy':   accuracy,
        'precision':  precision,
        'recall':     recall,
        'f1':         f1,
        'confusion_matrix': cm,
        'class_report':     cr,
    }


def get_feature_importance(pipeline, preprocessor, model_name):
    """Extract feature importance from RF or XGB models."""
    try:
        model = pipeline.named_steps['classifier']
        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_

            # Get feature names after preprocessing
            cat_names = pipeline.named_steps['preprocessor'].\
                named_transformers_['cat']['onehot'].\
                get_feature_names_out(CATEGORICAL_FEATURES).tolist()
            all_names = cat_names + NUMERICAL_FEATURES + BINARY_FEATURES

            importance_dict = {}
            for name, imp in zip(all_names, importances):
                importance_dict[name] = round(float(imp), 5)

            # Top 15 sorted
            sorted_imp = dict(sorted(importance_dict.items(),
                                     key=lambda x: x[1], reverse=True)[:15])
            return sorted_imp
    except Exception as e:
        pass
    return {}


# ─────────────────────────────────────────────────────────────────
# Main training loop
# ─────────────────────────────────────────────────────────────────

def train():
    print('=== AssureX ML Model Training ===\n')
    print('[1] Loading datasets...')
    train_df, val_df, test_df = load_data()

    # Combine train + val for final training (after selection)
    train_val_df = pd.concat([train_df, val_df], ignore_index=True)

    # Label encoding
    le = LabelEncoder()
    le.fit(['invalid_claim', 'manual_review', 'valid_claim'])
    print(f'  Classes: {list(le.classes_)}')

    # Encode labels
    y_train = le.transform(train_df[TARGET])
    y_val   = le.transform(val_df[TARGET])
    y_test  = le.transform(test_df[TARGET])
    y_trainval = le.transform(train_val_df[TARGET])

    X_train    = train_df[ALL_FEATURES]
    X_val      = val_df[ALL_FEATURES]
    X_test     = test_df[ALL_FEATURES]
    X_trainval = train_val_df[ALL_FEATURES]

    preprocessor = build_preprocessor()
    models       = get_models()

    print('\n[2] Training and evaluating 3 algorithms on validation set...')

    results = {}
    pipelines = {}

    for model_name, model in models.items():
        print(f'\n  Training: {model_name}')
        pipeline = Pipeline([
            ('preprocessor', preprocessor),
            ('classifier', model),
        ])

        # Fit on train only (evaluate on val)
        pipeline.fit(X_train, y_train)
        pipelines[model_name] = pipeline

        # Validation metrics
        val_metrics  = evaluate_model(model_name, pipeline, X_val, y_val, le)

        # 5-fold cross-validation on train+val
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        cv_scores = cross_val_score(
            Pipeline([('preprocessor', build_preprocessor()), ('classifier', model)]),
            X_trainval, y_trainval, cv=cv, scoring='accuracy', n_jobs=-1
        )
        val_metrics['cv_mean_accuracy'] = round(float(cv_scores.mean() * 100), 2)
        val_metrics['cv_std']           = round(float(cv_scores.std() * 100), 2)
        print(f'    CV Accuracy: {val_metrics["cv_mean_accuracy"]}% ± {val_metrics["cv_std"]}%')

        results[model_name] = val_metrics

    # ── Select best model (by validation accuracy) ──
    best_name = max(results, key=lambda k: results[k]['accuracy'])
    print(f'\n[3] Best model: {best_name} ({results[best_name]["accuracy"]}% val accuracy)')

    # ── Retrain best model on train+val, final test ──
    print('\n[4] Retraining best model on train+val, evaluating on UNSEEN test set...')
    final_preprocessor = build_preprocessor()
    best_pipeline = Pipeline([
        ('preprocessor', final_preprocessor),
        ('classifier',   models[best_name]),
    ])
    best_pipeline.fit(X_trainval, y_trainval)
    test_metrics = evaluate_model(best_name + ' (FINAL)', best_pipeline, X_test, y_test, le)
    results[best_name]['test_accuracy'] = test_metrics['accuracy']
    results[best_name]['test_metrics']  = test_metrics

    # Also run all other models on test for comparison report
    print('\n[5] Test set results for all models:')
    for model_name in models:
        if model_name != best_name:
            t_metrics = evaluate_model(model_name + ' (test)', pipelines[model_name], X_test, y_test, le)
            results[model_name]['test_accuracy'] = t_metrics['accuracy']
            results[model_name]['test_metrics']  = t_metrics

    # ── Save artifacts ──
    print('\n[6] Saving model artifacts...')

    # Save best model
    joblib.dump(best_pipeline, MODEL_DIR / 'assurex_model.pkl')
    print(f'  Saved: model/python_model/assurex_model.pkl')

    # Save preprocessor separately
    joblib.dump(final_preprocessor, MODEL_DIR / 'preprocessor.pkl')
    print(f'  Saved: model/python_model/preprocessor.pkl')

    # Save label encoder
    joblib.dump(le, MODEL_DIR / 'label_encoder.pkl')
    print(f'  Saved: model/python_model/label_encoder.pkl')

    # Save feature importance
    feat_imp = get_feature_importance(best_pipeline, final_preprocessor, best_name)
    with open(MODEL_DIR / 'feature_importance.json', 'w') as f:
        json.dump(feat_imp, f, indent=2)
    print(f'  Saved: model/python_model/feature_importance.json')

    # ── Model comparison report ──
    comparison = {
        'generated_at':  datetime.now().isoformat(),
        'best_model':    best_name,
        'target_accuracy': 85.0,
        'label_classes': list(le.classes_),
        'feature_count': len(ALL_FEATURES),
        'train_size':    len(train_df),
        'val_size':      len(val_df),
        'test_size':     len(test_df),
        'models':        results,
    }
    with open(MODEL_DIR / 'model_comparison.json', 'w') as f:
        json.dump(comparison, f, indent=2)
    print(f'  Saved: model/python_model/model_comparison.json')

    # ── Human-readable report ──
    _write_training_report(comparison, MODEL_DIR / 'training_report.txt')

    print('\n=== Training Complete ===')
    print(f'\nBest model: {best_name}')
    print(f'Validation accuracy: {results[best_name]["accuracy"]}%')
    print(f'Test accuracy:       {results[best_name]["test_accuracy"]}%')

    meets = results[best_name]['test_accuracy'] >= 85
    print(f'SRS 85% target: {"✓ MET" if meets else "✗ NOT MET"}')

    return best_pipeline, le, comparison


def _write_training_report(comparison: dict, path: Path):
    lines = [
        '=' * 60,
        'AssureX Claim Engine — ML Training Report',
        f'Generated: {comparison["generated_at"]}',
        '=' * 60,
        '',
        f'Dataset:',
        f'  Training:   {comparison["train_size"]} records',
        f'  Validation: {comparison["val_size"]} records',
        f'  Testing:    {comparison["test_size"]} records',
        f'  Classes:    {comparison["label_classes"]}',
        f'  Features:   {comparison["feature_count"]}',
        '',
        'Model Comparison:',
        '-' * 60,
    ]
    for model_name, metrics in comparison['models'].items():
        lines += [
            f'\n  {model_name}:',
            f'    Validation Accuracy:  {metrics["accuracy"]}%',
            f'    Validation F1-Score:  {metrics["f1"]}%',
            f'    CV Accuracy:          {metrics.get("cv_mean_accuracy","—")}% ± {metrics.get("cv_std","—")}%',
            f'    Test Accuracy:        {metrics.get("test_accuracy","—")}%',
        ]
        if 'test_metrics' in metrics:
            cr = metrics['test_metrics'].get('class_report', {})
            for cls in ['valid_claim', 'invalid_claim', 'manual_review']:
                if cls in cr:
                    lines.append(
                        f'      {cls:20s} P={cr[cls]["precision"]:.2f} '
                        f'R={cr[cls]["recall"]:.2f} F1={cr[cls]["f1-score"]:.2f}'
                    )
    lines += [
        '',
        '-' * 60,
        f'BEST MODEL: {comparison["best_model"]}',
        f'SRS 85% target: {"MET" if comparison["models"][comparison["best_model"]].get("test_accuracy", 0) >= 85 else "NOT MET"}',
        '=' * 60,
    ]
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f'  Saved: model/python_model/training_report.txt')


# ─────────────────────────────────────────────────────────────────
# Inference helper (used by decision engine)
# ─────────────────────────────────────────────────────────────────

def predict_claim(feature_dict: dict, model_path=None, le_path=None) -> dict:
    """
    Given a preprocessed feature dict, returns prediction + confidence scores.

    Returns:
        {
            'predicted_class': 'valid_claim' | 'invalid_claim' | 'manual_review',
            'confidence_valid': float,
            'confidence_invalid': float,
            'confidence_manual': float,
        }
    """
    model_path = model_path or MODEL_DIR / 'assurex_model.pkl'
    le_path    = le_path    or MODEL_DIR / 'label_encoder.pkl'

    pipeline = joblib.load(model_path)
    le       = joblib.load(le_path)

    # Build single-row DataFrame
    df = pd.DataFrame([feature_dict])

    # Ensure all expected columns present
    for col in ALL_FEATURES:
        if col not in df.columns:
            df[col] = 0

    df = df[ALL_FEATURES]

    proba         = pipeline.predict_proba(df)[0]
    pred_idx      = int(np.argmax(proba))
    pred_class    = le.inverse_transform([pred_idx])[0]
    classes       = le.classes_

    conf_dict = {cls: round(float(p) * 100, 2) for cls, p in zip(classes, proba)}
    return {
        'predicted_class':    pred_class,
        'confidence_valid':   conf_dict.get('valid_claim', 0.0),
        'confidence_invalid': conf_dict.get('invalid_claim', 0.0),
        'confidence_manual':  conf_dict.get('manual_review', 0.0),
        'top_confidence':     round(float(max(proba)) * 100, 2),
    }


if __name__ == '__main__':
    train()
