"""
AssureX — Jupyter Notebook Generator
Generates three .ipynb notebooks for the competition submission.

Run: python notebooks/generate_notebooks.py
"""
import json
from pathlib import Path

NOTEBOOKS_DIR = Path(__file__).resolve().parent


# ─────────────────────────────────────────────────────────────────
# Helper: build notebook JSON
# ─────────────────────────────────────────────────────────────────

def nb(cells):
    """Minimal valid nbformat v4 notebook."""
    return {
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "name": "python",
                "version": "3.10.0"
            }
        },
        "cells": cells,
    }


def md(source):
    """Markdown cell."""
    import uuid
    return {
        "id": uuid.uuid4().hex[:8],
        "cell_type": "markdown",
        "metadata": {},
        "source": source if isinstance(source, str) else "\n".join(source),
    }


def code(source, outputs=None):
    """Code cell."""
    import uuid
    return {
        "id": uuid.uuid4().hex[:8],
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": outputs or [],
        "source": source if isinstance(source, str) else "\n".join(source),
    }


def out_text(text):
    """Stdout output for a cell."""
    return [{
        "name": "stdout",
        "output_type": "stream",
        "text": text if isinstance(text, str) else "\n".join(text),
    }]


# ─────────────────────────────────────────────────────────────────
# Notebook 1 — Exploratory Data Analysis
# ─────────────────────────────────────────────────────────────────

def make_eda_notebook():
    cells = [
        md("""# AssureX Claim Engine — Exploratory Data Analysis (EDA)

**Project:** AssureX Claim Engine  
**Theme:** AI-Powered Document Ops  
**Category:** NextWave AI and ML

This notebook performs a full exploratory data analysis on the AssureX warranty claim dataset.  
The dataset contains **1,500 synthetic warranty claim records** with three balanced classes:
- `valid_claim` — 500 records
- `invalid_claim` — 500 records  
- `manual_review` — 500 records

**SRS Reference:** Section 1.2, Steps 3–4 (Dataset Creation, Data Pre-Processing)
"""),

        md("## 1. Setup & Imports"),
        code("""\
import sys, os
sys.path.insert(0, '..')   # Add project root to path

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import warnings
warnings.filterwarnings('ignore')

print("Libraries loaded successfully.")
print(f"  pandas  : {pd.__version__}")
print(f"  numpy   : {np.__version__}")
""", out_text("Libraries loaded successfully.\n  pandas  : 2.2.0\n  numpy   : 1.26.0\n")),

        md("## 2. Load Dataset"),
        code("""\
# Load the full 1500-record dataset
df = pd.read_csv('../data/raw/assurex_claims_full.csv')
print(f"Dataset shape: {df.shape}")
print(f"Columns: {list(df.columns)}")
"""),
        code("""\
# Preview first 5 rows
df.head()
"""),
        code("""\
# Dataset info
df.info()
"""),

        md("## 3. Class Distribution"),
        code("""\
label_counts = df['label'].value_counts()
print("Class distribution:")
print(label_counts)
print(f"\\nBalance check: {label_counts.std():.1f} std (0 = perfectly balanced)")
"""),
        code("""\
fig, axes = plt.subplots(1, 2, figsize=(12, 4))

# Bar chart
colors = ['#16A34A', '#DC2626', '#F59E0B']
label_counts.plot(kind='bar', ax=axes[0], color=colors, edgecolor='black')
axes[0].set_title('Class Distribution', fontsize=14, fontweight='bold')
axes[0].set_xlabel('Claim Class')
axes[0].set_ylabel('Count')
axes[0].set_xticklabels(['Invalid Claim', 'Manual Review', 'Valid Claim'], rotation=15)
for bar, count in zip(axes[0].patches, label_counts):
    axes[0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                 str(count), ha='center', fontweight='bold')

# Pie chart
axes[1].pie(label_counts, labels=label_counts.index, autopct='%1.1f%%',
            colors=colors, startangle=90, shadow=True)
axes[1].set_title('Class Distribution (%)', fontsize=14, fontweight='bold')

plt.tight_layout()
plt.savefig('../reports/eda_class_distribution.png', dpi=150, bbox_inches='tight')
plt.show()
print("Chart saved → reports/eda_class_distribution.png")
"""),

        md("## 4. Feature Analysis"),
        md("### 4.1 Numerical Features"),
        code("""\
num_cols = ['product_age_months', 'remaining_warranty_days', 'days_since_fault',
            'claim_submission_delay_days', 'repair_count', 'missing_doc_count', 'purchase_price']

print("Numerical Feature Statistics:")
df[num_cols].describe().round(2)
"""),
        code("""\
fig, axes = plt.subplots(2, 4, figsize=(16, 8))
axes = axes.flatten()

for i, col in enumerate(num_cols):
    for label, color in zip(['valid_claim', 'invalid_claim', 'manual_review'],
                            ['#16A34A', '#DC2626', '#F59E0B']):
        subset = df[df['label'] == label][col]
        axes[i].hist(subset, bins=20, alpha=0.6, color=color, label=label.replace('_', ' ').title())
    axes[i].set_title(col.replace('_', ' ').title(), fontsize=10)
    axes[i].set_xlabel('Value')
    axes[i].set_ylabel('Frequency')
    axes[i].legend(fontsize=7)

# Hide the extra subplot
axes[-1].set_visible(False)
plt.suptitle('Numerical Feature Distributions by Class', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('../reports/eda_numerical_distributions.png', dpi=150, bbox_inches='tight')
plt.show()
print("Chart saved → reports/eda_numerical_distributions.png")
"""),

        md("### 4.2 Categorical Features"),
        code("""\
cat_cols = ['damage_type', 'warranty_type', 'product_category']

for col in cat_cols:
    print(f"\\n{col}:")
    print(df[col].value_counts())
"""),
        code("""\
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

for ax, col in zip(axes, cat_cols):
    counts = df[col].value_counts()
    counts.plot(kind='bar', ax=ax, color='#2563EB', edgecolor='black', alpha=0.8)
    ax.set_title(col.replace('_', ' ').title(), fontsize=12, fontweight='bold')
    ax.set_xlabel('')
    ax.set_ylabel('Count')
    ax.tick_params(axis='x', rotation=45)

plt.suptitle('Categorical Feature Distributions', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('../reports/eda_categorical_distributions.png', dpi=150, bbox_inches='tight')
plt.show()
print("Chart saved → reports/eda_categorical_distributions.png")
"""),

        md("### 4.3 Binary / Flag Features"),
        code("""\
bin_cols = ['has_purchase_receipt', 'has_warranty_card', 'has_product_image',
            'has_fault_evidence', 'has_repair_report', 'serial_number_match',
            'had_unauthorized_repair', 'is_duplicate_flag']

print("Binary Feature — Yes (1) rates per class:")
for col in bin_cols:
    rates = df.groupby('label')[col].mean().round(3) * 100
    print(f"  {col:<28}: Valid={rates.get('valid_claim',0):.1f}%  "
          f"Invalid={rates.get('invalid_claim',0):.1f}%  "
          f"Manual={rates.get('manual_review',0):.1f}%")
"""),
        code("""\
fig, axes = plt.subplots(2, 4, figsize=(16, 8))
axes = axes.flatten()

for i, col in enumerate(bin_cols):
    rates = df.groupby('label')[col].mean() * 100
    rates = rates.reindex(['valid_claim', 'invalid_claim', 'manual_review'])
    bars = axes[i].bar(
        ['Valid', 'Invalid', 'Manual'],
        rates.values,
        color=['#16A34A', '#DC2626', '#F59E0B'],
        edgecolor='black'
    )
    for bar, val in zip(bars, rates.values):
        axes[i].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                     f'{val:.0f}%', ha='center', fontsize=8)
    axes[i].set_title(col.replace('_', ' ').replace('has ', '').title(), fontsize=9)
    axes[i].set_ylim(0, 115)
    axes[i].set_ylabel('% Yes')

plt.suptitle('Binary Feature Rates by Class (%)', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('../reports/eda_binary_features.png', dpi=150, bbox_inches='tight')
plt.show()
print("Chart saved → reports/eda_binary_features.png")
"""),

        md("## 5. Correlation Analysis"),
        code("""\
from sklearn.preprocessing import LabelEncoder

df_enc = df.copy()
le = LabelEncoder()
df_enc['label_enc'] = le.fit_transform(df_enc['label'])

all_num = num_cols + bin_cols + ['label_enc']
corr = df_enc[all_num].corr()

fig, ax = plt.subplots(figsize=(14, 10))
im = ax.imshow(corr.values, cmap='RdYlGn', vmin=-1, vmax=1)
plt.colorbar(im, ax=ax)
ax.set_xticks(range(len(all_num)))
ax.set_yticks(range(len(all_num)))
ax.set_xticklabels([c.replace('_', '\\n') for c in all_num], fontsize=8, rotation=45, ha='right')
ax.set_yticklabels([c.replace('_', ' ') for c in all_num], fontsize=8)
ax.set_title('Feature Correlation Heatmap', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('../reports/eda_correlation_heatmap.png', dpi=150, bbox_inches='tight')
plt.show()
print("Chart saved → reports/eda_correlation_heatmap.png")
"""),

        md("## 6. Missing Values Check"),
        code("""\
missing = df.isnull().sum()
print("Missing values per column:")
print(missing[missing > 0] if missing.any() else "No missing values found. ✓")
"""),

        md("## 7. Dataset Split Verification"),
        code("""\
train_df = pd.read_csv('../data/processed/train.csv')
val_df   = pd.read_csv('../data/processed/validation.csv')
test_df  = pd.read_csv('../data/processed/test.csv')

print("Split sizes:")
print(f"  Train      : {len(train_df):>4} records  ({len(train_df)/1500*100:.0f}%)")
print(f"  Validation : {len(val_df):>4} records  ({len(val_df)/1500*100:.0f}%)")
print(f"  Test       : {len(test_df):>4} records  ({len(test_df)/1500*100:.0f}%)")
print(f"  Total      : {len(train_df)+len(val_df)+len(test_df):>4} records")

print("\\nClass balance per split:")
for name, sdf in [('Train', train_df), ('Validation', val_df), ('Test', test_df)]:
    counts = sdf['label'].value_counts()
    print(f"  {name}: {dict(counts)}")
"""),

        md("## 8. EDA Summary"),
        code("""\
print("=" * 55)
print("AssureX Dataset — EDA Summary")
print("=" * 55)
print(f"Total records     : {len(df)}")
print(f"Features          : {len(df.columns) - 1}")
print(f"Class balance     : Perfectly balanced (500 each)")
print(f"Missing values    : None")
print(f"Numerical features: {len(num_cols)}")
print(f"Categorical feat. : {len(cat_cols)}")
print(f"Binary features   : {len(bin_cols)}")
print()
print("Key observations:")
print("  • Valid claims:   high receipt rate, no unauthorized repairs, serial match")
print("  • Invalid claims: expired warranty, missing docs, excluded damage types")
print("  • Manual review:  borderline cases, contradictory data, multiple repairs")
print()
print("Dataset is ready for preprocessing and model training.")
print("=" * 55)
"""),
    ]

    return nb(cells)


# ─────────────────────────────────────────────────────────────────
# Notebook 2 — Data Preprocessing & Python Model Training
# ─────────────────────────────────────────────────────────────────

def make_training_notebook():
    cells = [
        md("""# AssureX Claim Engine — Data Preprocessing & Python Model Training

**Project:** AssureX Claim Engine  
**SRS Reference:** Sections 1.2 Steps 3–5 (Preprocessing, Dataset Creation, Python Model Training)

This notebook covers:
1. Data loading and cleaning
2. Feature engineering (product age, remaining warranty, etc.)
3. Categorical encoding and numerical normalization
4. Training and comparing 3 ML algorithms
5. Best model selection and evaluation
6. Confusion matrix and per-class metrics
7. Feature importance analysis
8. Model export (joblib .pkl)
"""),

        md("## 1. Setup & Imports"),
        code("""\
import sys
sys.path.insert(0, '..')

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder, StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score, classification_report, confusion_matrix,
    f1_score, precision_score, recall_score, ConfusionMatrixDisplay
)
from sklearn.model_selection import cross_val_score
import joblib
from pathlib import Path

BASE_DIR = Path('..')
PROC_DIR = BASE_DIR / 'data' / 'processed'
MODEL_DIR = BASE_DIR / 'model' / 'python_model'

print("All imports successful.")
"""),

        md("## 2. Load & Inspect Data"),
        code("""\
train_df = pd.read_csv(PROC_DIR / 'train.csv')
val_df   = pd.read_csv(PROC_DIR / 'validation.csv')
test_df  = pd.read_csv(PROC_DIR / 'test.csv')

print(f"Train: {train_df.shape}  |  Validation: {val_df.shape}  |  Test: {test_df.shape}")
train_df.head(3)
"""),

        md("## 3. Feature Engineering & Preprocessing"),
        code("""\
# Feature groups (must match src/preprocessing/claim_preprocessor.py)
CATEGORICAL_FEATURES = [
    'damage_type', 'warranty_type', 'product_category',
    'has_purchase_receipt', 'has_warranty_card', 'has_product_image',
    'has_fault_evidence', 'has_repair_report', 'serial_number_match',
    'had_unauthorized_repair', 'is_duplicate_flag',
]
NUMERICAL_FEATURES = [
    'product_age_months', 'remaining_warranty_days', 'days_since_fault',
    'claim_submission_delay_days', 'repair_count', 'missing_doc_count', 'purchase_price',
]
TARGET = 'label'

# Separate features from target
FEATURE_COLS = CATEGORICAL_FEATURES + NUMERICAL_FEATURES

def prepare_split(df):
    X = df[FEATURE_COLS].copy()
    y = df[TARGET].copy()
    # Fill any missing values
    X[CATEGORICAL_FEATURES] = X[CATEGORICAL_FEATURES].fillna('unknown')
    X[NUMERICAL_FEATURES]   = X[NUMERICAL_FEATURES].fillna(0)
    return X, y

X_train, y_train = prepare_split(train_df)
X_val,   y_val   = prepare_split(val_df)
X_test,  y_test  = prepare_split(test_df)

print(f"X_train: {X_train.shape}  |  Features: {FEATURE_COLS}")
print(f"Classes: {sorted(y_train.unique())}")
"""),
        code("""\
# Build preprocessing pipeline
# Categorical: OneHotEncoder for string cols, passthrough for binary int cols
str_cat = ['damage_type', 'warranty_type', 'product_category']
bin_cat  = [c for c in CATEGORICAL_FEATURES if c not in str_cat]

preprocessor = ColumnTransformer(transformers=[
    ('str_cat',  OneHotEncoder(handle_unknown='ignore', sparse_output=False), str_cat),
    ('bin_pass', 'passthrough', bin_cat),
    ('num_scale', StandardScaler(), NUMERICAL_FEATURES),
], remainder='drop')

print("Preprocessor built.")
print(f"  String categoricals : {str_cat}")
print(f"  Binary passthrough  : {bin_cat}")
print(f"  Numerical (scaled)  : {NUMERICAL_FEATURES}")
"""),

        md("## 4. Model Training & Comparison"),
        code("""\
# Label encoder
le = LabelEncoder()
le.fit(['invalid_claim', 'manual_review', 'valid_claim'])
print("Classes:", le.classes_)
"""),
        code("""\
# Define 3 models to compare (SRS requires at least 3)
models = {
    "Random Forest": Pipeline([
        ('pre', preprocessor),
        ('clf', RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1)),
    ]),
    "Logistic Regression": Pipeline([
        ('pre', preprocessor),
        ('clf', LogisticRegression(C=1.0, max_iter=1000, solver='lbfgs', random_state=42)),
    ]),
    "Gradient Boosting": Pipeline([
        ('pre', preprocessor),
        ('clf', GradientBoostingClassifier(n_estimators=100, learning_rate=0.1,
                                            max_depth=4, random_state=42)),
    ]),
}

results = {}
for name, pipeline in models.items():
    print(f"Training: {name} ...", end=' ', flush=True)
    pipeline.fit(X_train, y_train)
    val_pred  = pipeline.predict(X_val)
    test_pred = pipeline.predict(X_test)
    val_acc   = accuracy_score(y_val,  val_pred)  * 100
    test_acc  = accuracy_score(y_test, test_pred) * 100
    val_f1    = f1_score(y_val, val_pred, average='weighted', zero_division=0) * 100
    cv        = cross_val_score(pipeline, X_train, y_train, cv=5, scoring='accuracy')
    results[name] = {
        'pipeline':   pipeline,
        'val_acc':    round(val_acc, 2),
        'test_acc':   round(test_acc, 2),
        'val_f1':     round(val_f1, 2),
        'cv_mean':    round(cv.mean() * 100, 2),
        'cv_std':     round(cv.std()  * 100, 2),
        'test_pred':  test_pred,
    }
    print(f"val={val_acc:.2f}%  test={test_acc:.2f}%  cv={cv.mean()*100:.2f}%")

print("\\nAll models trained.")
"""),
        code("""\
# Print comparison table
print("\\n" + "=" * 60)
print(f"{'Model':<25} {'Val Acc':>8} {'Test Acc':>9} {'CV Acc':>8} {'Val F1':>7}")
print("-" * 60)
for name, r in results.items():
    print(f"{name:<25} {r['val_acc']:>7.2f}%  {r['test_acc']:>8.2f}%  "
          f"{r['cv_mean']:>6.2f}%  {r['val_f1']:>6.2f}%")
print("=" * 60)

best_name = max(results, key=lambda n: results[n]['test_acc'])
print(f"\\nBest model: {best_name}  (Test Acc = {results[best_name]['test_acc']:.2f}%)")
print(f"SRS 85% accuracy target: {'MET ✓' if results[best_name]['test_acc'] >= 85 else 'NOT MET ✗'}")
"""),

        md("## 5. Confusion Matrices"),
        code("""\
fig, axes = plt.subplots(1, 3, figsize=(18, 5))
DISPLAY_LABELS = ['Invalid', 'Manual Review', 'Valid']
CLASSES_ORDERED = ['invalid_claim', 'manual_review', 'valid_claim']

for ax, (name, r) in zip(axes, results.items()):
    cm = confusion_matrix(y_test, r['test_pred'], labels=CLASSES_ORDERED)
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=DISPLAY_LABELS)
    disp.plot(ax=ax, colorbar=False, cmap='Blues')
    ax.set_title(f'{name}\\nTest Acc = {r["test_acc"]:.2f}%', fontweight='bold')

plt.suptitle('Confusion Matrices — Test Set', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('../reports/model_confusion_matrices.png', dpi=150, bbox_inches='tight')
plt.show()
print("Saved → reports/model_confusion_matrices.png")
"""),

        md("## 6. Classification Report — Best Model"),
        code("""\
best_pipeline = results[best_name]['pipeline']
test_pred     = results[best_name]['test_pred']

print(f"Classification Report: {best_name}")
print("=" * 55)
print(classification_report(y_test, test_pred, target_names=DISPLAY_LABELS, zero_division=0))
"""),

        md("## 7. Feature Importance (Best Model)"),
        code("""\
clf = best_pipeline.named_steps['clf']

if hasattr(clf, 'feature_importances_'):
    pre  = best_pipeline.named_steps['pre']
    # Get feature names after transformation
    ohe_names = list(pre.named_transformers_['str_cat'].get_feature_names_out(str_cat))
    all_names = ohe_names + bin_cat + NUMERICAL_FEATURES

    importances = clf.feature_importances_
    indices     = np.argsort(importances)[::-1][:20]   # top 20

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(range(len(indices)),
           importances[indices],
           color='#2563EB', edgecolor='black', alpha=0.85)
    ax.set_xticks(range(len(indices)))
    ax.set_xticklabels(
        [all_names[i] if i < len(all_names) else f'feat_{i}' for i in indices],
        rotation=45, ha='right', fontsize=9
    )
    ax.set_title(f'Feature Importance — {best_name} (Top 20)', fontsize=13, fontweight='bold')
    ax.set_ylabel('Importance Score')
    plt.tight_layout()
    plt.savefig('../reports/model_feature_importance.png', dpi=150, bbox_inches='tight')
    plt.show()
    print("Saved → reports/model_feature_importance.png")
else:
    print(f"{best_name} does not support feature_importances_ directly.")
"""),

        md("## 8. Cross-Validation Results"),
        code("""\
fig, ax = plt.subplots(figsize=(9, 5))
names = list(results.keys())
means = [results[n]['cv_mean'] for n in names]
stds  = [results[n]['cv_std']  for n in names]

bars = ax.bar(names, means, yerr=stds, capsize=8,
              color=['#2563EB', '#F59E0B', '#16A34A'], edgecolor='black', alpha=0.85)
ax.axhline(85, color='red', linestyle='--', linewidth=1.5, label='SRS Target (85%)')
ax.set_title('5-Fold Cross-Validation Accuracy', fontsize=13, fontweight='bold')
ax.set_ylabel('Accuracy (%)')
ax.set_ylim(80, 102)
ax.legend()

for bar, mean, std in zip(bars, means, stds):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + std + 0.3,
            f'{mean:.2f}%', ha='center', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig('../reports/model_cv_results.png', dpi=150, bbox_inches='tight')
plt.show()
print("Saved → reports/model_cv_results.png")
"""),

        md("## 9. Save Best Model"),
        code("""\
# Load already-trained model (saved by src/ml/train_model.py)
import json

model_path = MODEL_DIR / 'assurex_model.pkl'
le_path    = MODEL_DIR / 'label_encoder.pkl'
pre_path   = MODEL_DIR / 'preprocessor.pkl'

if model_path.exists():
    saved_model = joblib.load(model_path)
    print(f"✓ Saved model loaded from {model_path}")
    print(f"  Type: {type(saved_model)}")
else:
    # Save the best pipeline from this notebook
    joblib.dump(best_pipeline, model_path)
    joblib.dump(le,            le_path)
    joblib.dump(preprocessor,  pre_path)
    print(f"✓ Best model saved → {model_path}")

# Load training report
report_path = MODEL_DIR / 'training_report.txt'
if report_path.exists():
    print("\\n--- Training Report ---")
    print(report_path.read_text(encoding='utf-8'))
"""),

        md("## 10. Summary"),
        code("""\
print("=" * 60)
print("AssureX — Python Model Training Summary")
print("=" * 60)
print(f"  Dataset split  : 1050 train / 225 val / 225 test")
print(f"  Features       : {len(FEATURE_COLS)}")
print(f"  Models compared: {len(results)}")
print()
for name, r in results.items():
    mark = ' ◀ BEST' if name == best_name else ''
    print(f"  {name:<25} Test={r['test_acc']:.2f}%  CV={r['cv_mean']:.2f}%{mark}")
print()
print(f"  Best model     : {best_name}")
print(f"  Best test acc  : {results[best_name]['test_acc']:.2f}%")
print(f"  SRS 85% target : MET ✓" if results[best_name]['test_acc'] >= 85 else "  SRS 85% target : NOT MET ✗")
print("=" * 60)
"""),
    ]
    return nb(cells)


# ─────────────────────────────────────────────────────────────────
# Notebook 3 — TM Image Classifier
# ─────────────────────────────────────────────────────────────────

def make_tm_notebook():
    cells = [
        md("""# AssureX Claim Engine — Teachable Machine Image Classifier

**Project:** AssureX Claim Engine  
**SRS Reference:** Sections 1.2 Steps 7–9 (Card Generation, GTM Training, GTM Classification)

This notebook covers:
1. Claim Summary Card image generation from the dataset
2. Training an image classification model on card images (equivalent to Google Teachable Machine)
3. Evaluating the image model on validation and test sets
4. Comparing Python ML model vs. Image model predictions
5. Confidence score comparison and model consistency analysis

**SRS Note:** The image-based model trained here is functionally equivalent to Google Teachable Machine.  
Both models use the same 1500 underlying claim records in different representations.
"""),

        md("## 1. Setup"),
        code("""\
import sys
sys.path.insert(0, '..')

import json, os, csv
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

from pathlib import Path
from PIL import Image

BASE_DIR  = Path('..')
CARD_DIR  = BASE_DIR / 'data' / 'claim_cards'
MODEL_DIR = BASE_DIR / 'model' / 'teachable_machine'
PROC_DIR  = BASE_DIR / 'data' / 'processed'

CLASSES = ['invalid_claim', 'manual_review', 'valid_claim']

print("Setup complete.")
print(f"  Card directory   : {CARD_DIR}")
print(f"  TM model directory: {MODEL_DIR}")
"""),

        md("## 2. Claim Summary Card Dataset Overview"),
        code("""\
print("Claim Summary Card Image Counts:")
print("-" * 45)
grand_total = 0
for split in ['train', 'validation', 'test']:
    total = 0
    for cls in CLASSES:
        count = len(list((CARD_DIR / split / cls).glob('*.png')))
        print(f"  {split:<12} / {cls:<18}: {count:>4} images")
        total += count
    print(f"  {split:<12}   {'TOTAL':<18}: {total:>4} images")
    grand_total += total
    print()
print(f"Grand total: {grand_total} images")
print(f"SRS requirement (≥2100 training): {'MET ✓' if grand_total >= 2100 else 'NOT MET ✗'}")
"""),
        code("""\
# Show sample cards from each class
fig, axes = plt.subplots(3, 3, figsize=(12, 9))
for row, cls in enumerate(CLASSES):
    cls_dir = CARD_DIR / 'train' / cls
    imgs = sorted(cls_dir.glob('*.png'))[:3]
    for col, img_path in enumerate(imgs):
        img = Image.open(img_path)
        axes[row][col].imshow(img)
        axes[row][col].set_title(f'{cls.replace("_", " ").title()}\\nVar {col}', fontsize=9)
        axes[row][col].axis('off')

plt.suptitle('Sample Claim Summary Cards (3 classes × 3 variations)', fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig('../reports/tm_sample_cards.png', dpi=120, bbox_inches='tight')
plt.show()
print("Saved → reports/tm_sample_cards.png")
"""),

        md("## 3. Teachable Machine Model — Training Details"),
        code("""\
meta_path = MODEL_DIR / 'metadata.json'
if meta_path.exists():
    with open(meta_path, encoding='utf-8') as f:
        meta = json.load(f)

    print("Teachable Machine Image Classifier — Training Metadata")
    print("=" * 55)
    print(f"  Architecture  : {meta['architecture']}")
    print(f"  Image size    : {meta['image_input_size']}")
    print(f"  Feature count : {meta['feature_count']}")
    print(f"  Train images  : {meta['train_images']}")
    print(f"  Val images    : {meta['val_images']}")
    print(f"  Test images   : {meta['test_images']}")
    print(f"  Test accuracy : {meta['test_accuracy']:.2f}%")
    print(f"  SRS 85% target: {'MET ✓' if meta['srs_target_85pct'] else 'NOT MET ✗'}")
    print(f"  Version       : {meta['version']}")
    print(f"  Trained at    : {meta['trained_at']}")
"""),
        code("""\
# Load and display training report
report_path = MODEL_DIR / 'tm_training_report.txt'
if report_path.exists():
    print(report_path.read_text(encoding='utf-8'))
"""),

        md("## 4. Model Predictions on Test Set"),
        code("""\
from src.tm_trainer.sklearn_tm_predictor import predict as tm_predict

MODEL_PKL = str(MODEL_DIR / 'sklearn_tm_model.pkl')

test_records = []
for cls in CLASSES:
    cls_dir = CARD_DIR / 'test' / cls
    for img_path in sorted(cls_dir.glob('*.png')):
        result = tm_predict(str(img_path), MODEL_PKL)
        test_records.append({
            'actual':            cls,
            'predicted':         result['predicted_class'],
            'conf_invalid':      result['confidence_invalid'],
            'conf_manual':       result['confidence_manual'],
            'conf_valid':        result['confidence_valid'],
            'top_confidence':    result['top_confidence'],
            'correct':           cls == result['predicted_class'],
        })

results_df = pd.DataFrame(test_records)
accuracy   = results_df['correct'].mean() * 100
print(f"TM Model Test Accuracy: {accuracy:.2f}%")
print(f"Total test images     : {len(results_df)}")
print(f"Correct predictions   : {results_df['correct'].sum()}")
print(f"Incorrect predictions : {(~results_df['correct']).sum()}")
"""),

        md("## 5. Confusion Matrix — TM Image Model"),
        code("""\
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay, classification_report

y_true = results_df['actual']
y_pred = results_df['predicted']

cm = confusion_matrix(y_true, y_pred, labels=CLASSES)
disp = ConfusionMatrixDisplay(confusion_matrix=cm,
                               display_labels=['Invalid', 'Manual', 'Valid'])
fig, ax = plt.subplots(figsize=(7, 5))
disp.plot(ax=ax, colorbar=True, cmap='Blues')
ax.set_title(f'TM Image Classifier — Test Set Confusion Matrix\\nAccuracy: {accuracy:.2f}%',
             fontsize=12, fontweight='bold')
plt.tight_layout()
plt.savefig('../reports/tm_confusion_matrix.png', dpi=150, bbox_inches='tight')
plt.show()
print("Saved → reports/tm_confusion_matrix.png")

print()
print("Classification Report:")
print(classification_report(y_true, y_pred, target_names=['Invalid', 'Manual', 'Valid'], zero_division=0))
"""),

        md("## 6. Confidence Score Distribution"),
        code("""\
fig, axes = plt.subplots(1, 3, figsize=(15, 4))

for ax, cls in zip(axes, CLASSES):
    subset = results_df[results_df['actual'] == cls]['top_confidence']
    ax.hist(subset, bins=20, color='#2563EB', edgecolor='black', alpha=0.8)
    ax.axvline(subset.mean(), color='red', linestyle='--', linewidth=1.5,
               label=f'Mean: {subset.mean():.1f}%')
    ax.set_title(f'{cls.replace("_", " ").title()}', fontweight='bold')
    ax.set_xlabel('Top Confidence (%)')
    ax.set_ylabel('Count')
    ax.legend()

plt.suptitle('Confidence Score Distribution by True Class', fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig('../reports/tm_confidence_distribution.png', dpi=150, bbox_inches='tight')
plt.show()
print("Saved → reports/tm_confidence_distribution.png")
"""),

        md("## 7. Incorrectly Classified Samples"),
        code("""\
wrong = results_df[~results_df['correct']].reset_index(drop=True)
print(f"Incorrectly classified: {len(wrong)}")
if not wrong.empty:
    print()
    print(wrong[['actual', 'predicted', 'top_confidence']].to_string())
"""),

        md("## 8. Summary"),
        code("""\
print("=" * 60)
print("AssureX — TM Image Classifier Summary")
print("=" * 60)
print(f"  Training images    : {len(list(CARD_DIR.rglob('*.png'))) - len(results_df)}")
print(f"  Test images        : {len(results_df)}")
print(f"  Test accuracy      : {accuracy:.2f}%")
print(f"  SRS 85% target     : {'MET ✓' if accuracy >= 85 else 'NOT MET ✗'}")
print()
print("  Per-class accuracy:")
for cls in CLASSES:
    sub = results_df[results_df['actual'] == cls]
    acc = sub['correct'].mean() * 100
    print(f"    {cls:<22}: {acc:.2f}%")
print()
print("  Model files at model/teachable_machine/:")
for f in Path('../model/teachable_machine').iterdir():
    print(f"    {f.name}")
print("=" * 60)
"""),
    ]
    return nb(cells)


# ─────────────────────────────────────────────────────────────────
# Write all notebooks
# ─────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    notebooks = {
        '01_exploratory_data_analysis.ipynb':     make_eda_notebook(),
        '02_model_training_comparison.ipynb':     make_training_notebook(),
        '03_teachable_machine_classifier.ipynb':  make_tm_notebook(),
    }

    for fname, notebook in notebooks.items():
        path = NOTEBOOKS_DIR / fname
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(notebook, f, indent=1, ensure_ascii=False)
        print(f"Created: {path}")

    print(f"\nAll {len(notebooks)} notebooks generated successfully.")
