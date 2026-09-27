# AssureX Claim Engine — Developer Guide

**Version:** 1.0 · **Date:** September 2026
**Team:** Muhammad Hunain · Mariha Ashfaq · Owais Ahmed · Muhammad Daniyal
**Competition:** TechWiz 7 — Aptech Computer Education

---

## Table of Contents

1. [System Architecture](#1-system-architecture)
2. [Project Structure](#2-project-structure)
3. [Database Design](#3-database-design)
4. [Django Apps](#4-django-apps)
5. [AI Pipeline](#5-ai-pipeline)
6. [Rule Engine](#6-rule-engine)
7. [OCR Pipeline](#7-ocr-pipeline)
8. [Decision Engine](#8-decision-engine)
9. [Setup & Installation](#9-setup--installation)
10. [Running Tests](#10-running-tests)
11. [Diagrams](#11-diagrams)

---

## 1. System Architecture

AssureX follows a layered architecture:

```
┌─────────────────────────────────────────────────────┐
│                   Web Layer (Django)                 │
│  accounts │ products │ warranties │ claims           │
│  reviewer │ administrator │ notifications            │
├─────────────────────────────────────────────────────┤
│                  AI Pipeline (src/)                  │
│  ocr → preprocessing → ml → card_generator          │
│  tm_trainer → rule_engine → decision_engine          │
├─────────────────────────────────────────────────────┤
│               Data Layer (SQLite/PostgreSQL)         │
│  16 tables — users, products, warranties, claims...  │
├─────────────────────────────────────────────────────┤
│                  Model Layer (model/)                │
│  python_model/ (pkl files) │ teachable_machine/      │
└─────────────────────────────────────────────────────┘
```

### Key Design Decisions

1. **Dual-model architecture** — Python ML (tabular) + GTM (image) run independently and results are compared
2. **src/ separation** — All AI logic is framework-independent Python, testable without Django
3. **Configurable rules** — Warranty rules are JSON files, not hardcoded
4. **Role-based access** — 4 roles with decorator-enforced permissions

---

## 2. Project Structure

```
AssureX/
├── assurex/                    # Django settings package
│   ├── settings/
│   │   ├── base.py             # Shared settings
│   │   ├── development.py      # Dev: SQLite, DEBUG=True
│   │   └── production.py       # Prod: PostgreSQL, DEBUG=False
│   ├── urls.py                 # Root URL configuration
│   └── wsgi.py
│
├── apps/                       # Django applications
│   ├── accounts/               # Auth, user model, profiles
│   ├── products/               # Product registration
│   ├── warranties/             # Warranty records & policies
│   ├── claims/                 # Claim wizard, OCR, AI pipeline
│   ├── reviewer/               # Manual review workflow
│   ├── administrator/          # Admin dashboard & analytics
│   └── notifications/          # In-app notifications
│
├── src/                        # AI pipeline modules
│   ├── ocr/                    # Tesseract + EasyOCR extraction
│   ├── preprocessing/          # Feature engineering
│   ├── ml/                     # Model training & inference
│   ├── card_generator/         # Claim Summary Card generator
│   ├── tm_trainer/             # GTM proxy model training
│   ├── rule_engine/            # Warranty rule validation
│   └── decision_engine/        # Final decision orchestrator
│
├── model/
│   ├── python_model/           # assurex_model.pkl, preprocessor.pkl
│   └── teachable_machine/      # sklearn_tm_model.pkl, labels.txt
│
├── data/
│   ├── raw/                    # Full 1,500-record dataset
│   └── processed/              # Train/val/test splits
│
├── policies/                   # JSON warranty policy files
├── dataset_generator/          # Synthetic data scripts
├── database/                   # Seed scripts, migrations helper
├── tests/                      # Automated test suite
├── templates/                  # Django HTML templates
├── static/                     # CSS, JS, images
├── documentation/              # All project documentation
├── screenshots/                # Application screenshots
└── reports/                    # Generated reports
```

---

## 3. Database Design

### Entity Relationships

```
users ──< products ──< warranties
  │           │
  │           └──< claims ──< claim_documents ──< ocr_results
  │                    │
  │                    ├──< repair_history
  │                    ├──< model_predictions
  │                    ├──< rule_results
  │                    └──1 reviews
  │
warranty_policies ──< warranties
product_categories ──< products
product_categories ──< warranty_policies
model_versions ──< model_predictions
users ──< notifications
users ──< audit_logs
system_configuration (standalone)
```

### 16 Tables Summary

| # | Table | Key Purpose |
|---|-------|-------------|
| 1 | users | Custom user model with 4 roles |
| 2 | product_categories | AC, Fridge, Smartphone, etc. |
| 3 | products | Customer-registered products |
| 4 | warranties | Warranty records per product |
| 5 | claims | Core claim records (38 columns) |
| 6 | claim_documents | Uploaded files per claim |
| 7 | ocr_results | Extracted data from documents |
| 8 | repair_history | Prior repair records |
| 9 | model_predictions | AI model predictions per claim |
| 10 | warranty_policies | Configurable warranty rules |
| 11 | rule_results | Rule engine check results |
| 12 | reviews | Reviewer decisions |
| 13 | notifications | In-app notifications |
| 14 | audit_logs | Complete action audit trail |
| 15 | model_versions | ML model version registry |
| 16 | system_configuration | Configurable system settings |

---

## 4. Django Apps

### 4.1 accounts

```
apps/accounts/
├── models.py          # User model (AbstractBaseUser), AuditLog
├── views.py           # Login, Register, Profile, Password Reset
├── decorators.py      # @customer_required, @employee_required, etc.
├── context_processors.py  # unread_notifications_count, user_role
└── templatetags/
    └── assurex_tags.py    # Custom template filters
```

**Custom User Model:**
```python
class User(AbstractBaseUser, PermissionsMixin):
    ROLES = ['customer', 'employee', 'reviewer', 'administrator']
    email = models.EmailField(unique=True)  # USERNAME_FIELD
    role  = models.CharField(max_length=20)
```

**Role Decorators:**
```python
@customer_required   # Only customers
@employee_required   # Only employees
@reviewer_required   # Only reviewers
@admin_required      # Only administrators
@employee_or_admin   # Employee OR admin
```

---

### 4.2 claims

The most complex app — handles the full claim lifecycle.

```
apps/claims/
├── models.py           # Claim, ClaimDocument, OCRResult,
│                       # RepairHistory, ModelPrediction, Review
├── views_submit.py     # 4-step claim wizard + contradiction detection
├── views_customer.py   # My claims list, claim detail
├── views_employee.py   # Employee dashboard, customer search
└── forms.py            # ClaimSubmitForm, DocumentUploadForm
```

**Claim Submission Flow:**
```
Step 1 (views_submit.claim_submit_step1)
  → Create Draft Claim

Step 2 (views_submit.claim_submit_step2)
  → Upload documents → Run OCR → SHA-256 hash

Step 3 (views_submit.claim_submit_step3)
  → Add repair history (optional)

Step 4 (views_submit.claim_submit_step4)
  → Contradiction detection → Submit
  → _trigger_ai_pipeline(claim)
```

**SHA-256 Duplicate Detection:**
```python
def _compute_hash(file_obj) -> str:
    sha256 = hashlib.sha256()
    for chunk in iter(lambda: file_obj.read(8192), b''):
        sha256.update(chunk)
    return sha256.hexdigest()
```

---

### 4.3 administrator

```
apps/administrator/
├── models.py      # SystemConfiguration
├── views.py       # Dashboard, UserMgmt, Analytics,
│                  # ModelVersions, Thresholds, Policies,
│                  # Reports, AuditLogs, Monitoring
└── urls.py
```

**SystemConfiguration — Dynamic Settings:**
```python
class SystemConfiguration(models.Model):
    key        = models.CharField(unique=True)
    value      = models.TextField()
    value_type = models.CharField()  # str/int/float/bool/json

    @classmethod
    def get(cls, key, default=None):
        # Returns typed value from DB
```

---

## 5. AI Pipeline

### 5.1 Overview

```
Claim Submitted
      │
      ▼
src/preprocessing/feature_extractor.py
  → Extracts 19 features from claim
      │
      ├──────────────────────────────┐
      ▼                              ▼
src/ml/predictor.py          src/card_generator/
  Python ML Model              claim_card_generator.py
  (Random Forest)              → Generates 600×420 PNG
      │                              │
      ▼                              ▼
  Python Prediction            src/tm_trainer/
  + Confidence Scores          tm_predictor.py
                                 GTM Model
                                    │
                                    ▼
                              TM Prediction
                              + Confidence Scores
                                    │
      ┌─────────────────────────────┘
      ▼
src/decision_engine/evaluator.py
  → Compare predictions
  → Run rule engine
  → Final decision
```

---

### 5.2 Feature Extraction (19 Features)

```python
# src/preprocessing/feature_extractor.py

def extract_features(claim) -> dict:
    return {
        # Categorical (OneHotEncoded)
        'product_category':           claim.product.category.name,
        'brand':                      claim.product.brand,
        'damage_type':                claim.damage_type,
        'warranty_type':              warranty.warranty_type,

        # Numerical (StandardScaled)
        'product_age_months':         product_age_months,
        'warranty_remaining_days':    remaining_days,
        'days_since_fault':           days_since_fault,
        'purchase_price_pkr':         float(claim.product.purchase_price or 0),
        'repair_count':               repair_count,
        'missing_documents_count':    missing_doc_count,
        'claim_submission_delay':     submission_delay,

        # Binary (pass-through)
        'has_receipt':                int(has_receipt),
        'has_warranty_card':          int(has_warranty_card),
        'has_product_image':          int(has_product_image),
        'has_fault_evidence':         int(has_fault_evidence),
        'has_unauthorized_repair':    int(unauthorized_repair),
        'is_warranty_active':         int(warranty_active),
        'serial_number_match':        int(serial_match),
        'is_duplicate_flag':          int(claim.is_duplicate),
    }
```

---

### 5.3 Python ML Model

```python
# src/ml/predictor.py

def predict(features: dict) -> dict:
    preprocessor = joblib.load(PREPROCESSOR_PATH)
    model        = joblib.load(MODEL_PATH)
    encoder      = joblib.load(ENCODER_PATH)

    df = pd.DataFrame([features])
    X  = preprocessor.transform(df)
    proba = model.predict_proba(X)[0]
    classes = encoder.classes_  # ['invalid_claim','manual_review','valid_claim']

    return {
        'predicted_class':      classes[proba.argmax()],
        'confidence_valid':     float(proba[classes=='valid_claim']),
        'confidence_invalid':   float(proba[classes=='invalid_claim']),
        'confidence_manual':    float(proba[classes=='manual_review']),
    }
```

**Training (3 algorithms compared):**
```bash
python src/ml/train_model.py
# Output: training_report.txt with accuracy table
# Best: Random Forest — 98.22% test accuracy
```

---

### 5.4 Claim Summary Card Generator

```python
# src/card_generator/claim_card_generator.py

def generate_claim_card(claim) -> str:
    """Generate 600x420 PNG — does NOT include ML predictions."""
    img = Image.new('RGB', (600, 420), color='#003631')
    draw = ImageDraw.Draw(img)

    # Sections: Header, Product Info, Warranty Status,
    #           Document Status, Fault Info, Summary
    # Color coding: Green=OK, Yellow=Warning, Red=Missing/Expired

    path = f'media/claim_cards/{claim.claim_reference}.png'
    img.save(path)
    return path
```

> ⚠️ Card must NOT show Python model prediction or confidence score.

---

### 5.5 GTM Proxy Model

```python
# src/tm_trainer/tm_predictor.py

def predict_from_card(image_path: str) -> dict:
    """Extract 278 visual features from card image."""
    img = cv2.imread(image_path)

    features = []
    # Color histograms (RGB channels, 32 bins each = 96)
    # Region pixel averages (6 regions × 3 channels = 18)
    # Texture features (LBP = 26 per region × 6 = 156)
    # Edge density (8)
    # Total: 278 features

    model = joblib.load(TM_MODEL_PATH)
    proba = model.predict_proba([features])[0]

    return {
        'predicted_class':    classes[proba.argmax()],
        'confidence_valid':   float(proba[0]),
        'confidence_invalid': float(proba[1]),
        'confidence_manual':  float(proba[2]),
    }
```

---

## 6. Rule Engine

```python
# src/rule_engine/warranty_rule_engine.py

RULES = [
    _check_warranty_active,           # Hard fail if expired
    _check_claim_reporting_period,    # Hard fail if > 14 days
    _check_purchase_proof,            # Warning if no receipt
    _check_serial_number,             # Manual review if mismatch
    _check_unauthorized_repair,       # Warning if unauthorized
    _check_excluded_damage,           # Hard fail if excluded type
    _check_duplicate_claim,           # Hard fail if duplicate
    _check_missing_documents,         # Warning per missing doc
    _check_repair_count,              # Warning if > 2 repairs
    _check_product_age,               # Warning if > 10 years
    _check_date_contradiction,        # Hard fail if contradictions
]

def run_rule_engine(claim_data: dict, policy: dict) -> RuleEngineResult:
    results = [rule(claim_data) for rule in RULES]
    return RuleEngineResult(results)
```

**Rule Severity Levels:**

| Severity | Effect |
|----------|--------|
| `hard_fail` | Claim → Likely Invalid (regardless of AI) |
| `warning` | Flagged but not blocking |
| `manual_review` | Claim → Manual Review queue |

**Policy Files** (`policies/`):
```json
{
  "name": "Smartphone Warranty Policy",
  "product_category": "Smartphone",
  "standard_duration_months": 12,
  "claim_reporting_period_days": 14,
  "covered_faults": ["electrical", "manufacturing", "display", "battery"],
  "exclusions": ["physical", "water"],
  "mandatory_documents": ["purchase_receipt", "product_image", "fault_evidence"],
  "max_repair_count": 2,
  "grace_period_days": 7
}
```

---

## 7. OCR Pipeline

```python
# src/ocr/extractor.py

def extract_document_data(file_path: str) -> dict:
    # Primary: Tesseract 5
    text = pytesseract.image_to_string(img, config='--psm 6')
    confidence = get_tesseract_confidence(img)

    # Fallback: EasyOCR if confidence < 0.5
    if confidence < 0.5:
        reader = easyocr.Reader(['en'])
        results = reader.readtext(file_path)
        text = ' '.join([r[1] for r in results])

    # Field extraction via regex
    return {
        'invoice_number': extract_invoice(text),
        'serial_number':  extract_serial(text),
        'purchase_date':  extract_date(text),
        'purchase_amount':extract_price(text),
        'retailer':       extract_retailer(text),
        'confidence':     confidence,
    }
```

**Key Regex Patterns:**
```python
DATE_PATTERN   = re.compile(r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})')
PRICE_PATTERN  = re.compile(r'(?:Rs\.?|PKR)\s?([\d,]+(?:\.\d{2})?)')
SERIAL_PATTERN = re.compile(r'S(?:erial|/N)[:\s#]*([A-Z0-9\-]{6,})', re.IGNORECASE)
```

---

## 8. Decision Engine

```python
# src/decision_engine/evaluator.py

def evaluate_claim(claim: Claim):
    # Step 1: Extract features
    features = extract_features(claim)

    # Step 2: Python ML prediction
    py_result = predict(features)

    # Step 3: Generate Claim Summary Card
    card_path = generate_claim_card(claim)

    # Step 4: GTM prediction
    tm_result = predict_from_card(card_path)

    # Step 5: Compare predictions
    conf_diff = abs(py_result['confidence_' + py_result['predicted_class'].split('_')[0]]
                  - tm_result['confidence_' + tm_result['predicted_class'].split('_')[0]]) * 100

    consistency = classify_consistency(
        py_pred=py_result['predicted_class'],
        tm_pred=tm_result['predicted_class'],
        conf_diff=conf_diff
    )

    # Step 6: Run rule engine
    policy = load_policy_for_claim(features)
    rule_result = run_rule_engine(features, policy)

    # Step 7: Final decision
    final = make_final_decision(py_result, tm_result, consistency, rule_result)

    # Step 8: Save to DB
    save_results_to_claim(claim, py_result, tm_result, conf_diff,
                          consistency, rule_result, final)
```

**Consistency Classification:**

| Condition | Status |
|-----------|--------|
| Same class, diff ≤ 5% | `strong_match` |
| Same class, diff 5–15% | `acceptable_match` |
| Same class, diff 15–25% | `weak_match` |
| Different classes | `model_disagreement` |
| Either model < 70% confidence | `uncertain_result` |

---

## 9. Setup & Installation

### Prerequisites

- Python 3.11+
- Git
- Tesseract OCR 5.x

### Step-by-Step Setup

```bash
# 1. Clone repository
git clone https://github.com/YOUR_USERNAME/assurex-claim-engine.git
cd assurex-claim-engine

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set environment variables
copy .env .env.local
# Edit .env with your SECRET_KEY

# 5. Run migrations
python manage.py makemigrations
python manage.py migrate

# 6. Seed initial data
python database/seed_data.py
python database/load_policies.py
python database/register_model_version.py

# 7. Collect static files
python manage.py collectstatic --noinput

# 8. Start server
python manage.py runserver
```

### Environment Variables

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DJANGO_SETTINGS_MODULE=assurex.settings.development
TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe
```

### Train ML Models

```bash
# Generate dataset
python dataset_generator/generate_dataset.py

# Train Python ML model
python src/ml/train_model.py

# Generate Claim Summary Cards
python src/card_generator/claim_card_generator.py

# Train GTM proxy model
python src/tm_trainer/train_tm_model.py
```

---

## 10. Running Tests

```bash
# Run all 180 tests
python -m pytest tests/ -v

# Run specific module
python -m pytest tests/test_rule_engine.py -v
python -m pytest tests/test_ml_model.py -v
python -m pytest tests/test_claim_submission.py -v

# Run with coverage
python -m pytest tests/ --cov=apps --cov=src --cov-report=html
```

**Test Files:**

| File | Tests | Coverage |
|------|-------|----------|
| test_authentication.py | 18 | Login, register, roles, decorators |
| test_product_warranty.py | 16 | Product CRUD, warranty tracking |
| test_claim_submission.py | 24 | 4-step wizard, validation |
| test_ocr.py | 14 | Extraction, field parsing |
| test_ml_model.py | 22 | Accuracy, features, confidence |
| test_rule_engine.py | 28 | All 11 rules, all SRS scenarios |
| test_decision_engine.py | 20 | Comparison, consistency tiers |
| test_reviewer.py | 16 | Queue, decisions, overrides |
| test_admin.py | 14 | Dashboard, export, thresholds |
| test_security.py | 8 | CSRF, XSS, SQL injection |

---

## 11. Diagrams

All diagrams are in `documentation/diagrams/` as `.xml` files importable into [diagrams.net](https://diagrams.net).

| Diagram | File |
|---------|------|
| System Architecture | `diagrams/system_architecture.xml` |
| ER Diagram (16 tables) | `diagrams/er_diagram.xml` |
| DFD Level 0 | `diagrams/dfd_level0.xml` |
| DFD Level 1 | `diagrams/dfd_level1.xml` |
| Use Case Diagram | `diagrams/use_case.xml` |
| Activity Diagram | `diagrams/activity_diagram.xml` |
| Sequence Diagram | `diagrams/sequence_diagram.xml` |
| Decision Flow | `diagrams/decision_flow.xml` |

**To open a diagram:**
1. Go to [diagrams.net](https://diagrams.net)
2. Click **"Open from"** → **"This device"**
3. Select the `.xml` file
4. Export as PNG/PDF for the report

---

*AssureX Claim Engine — Developer Guide v1.0 · TechWiz 7 · Aptech Computer Education · 2026*
