# AssureX Claim Engine — Project Report

**Project Name:** AssureX Claim Engine  
**Theme:** AI-Powered Document Ops  
**Category:** NextWave AI and ML  
**Version:** 1.0  
**Framework:** Django 4.2 (Python)  
**Competition:** TechWiz 7 — Aptech Limited

---

## Team Members

| Name | Student ID | Role |
|---|---|---|
| Muhammad Hunain | 1538835 | Lead Developer — Backend, AI Pipeline, Decision Engine |
| Mariha Ashfaq | 1540161 | ML Model Training, Dataset Generation, OCR Integration |
| Owais Ahmed | 1515897 | Frontend, Templates, Dashboard UI, Testing |
| Muhammad Daniyal | 1542905 | Rule Engine, Warranty Policies, Database Design |

**Institute:** Aptech Computer Education  
**Submission Date:** September 2026

---

## 1. Problem Definition

Warranty claim management is a critical yet error-prone process for manufacturers and service centers. Traditional manual evaluation requires staff to examine purchase details, product age, fault descriptions, repair history, warranty conditions, and supporting documents — a process that is time-consuming, inconsistent, and susceptible to duplicate or fraudulent claims.

---

## 2. Background and Business Necessity

- Manual warranty evaluation leads to inconsistent decisions and approval delays.
- Duplicate claims and overlooked exclusions result in financial losses.
- Customers experience long wait times with no transparency into claim status.
- Service centers need a faster, more reliable way to triage and process claims.

**The AssureX Claim Engine solves this by:**
- Automating claim validation using Python ML + Google Teachable Machine (GTM)
- Applying configurable warranty rule policies per product category
- Routing uncertain or conflicting claims to human reviewers
- Providing full audit trails and real-time status tracking

---

## 3. Proposed Solution

An AI-powered, web-based warranty claim validation system using:

1. **Python Classification Model** — Random Forest (98.22% accuracy) trained on 1,500 synthetic warranty claim records
2. **Teachable Machine Image Model** — Gradient Boosting on Claim Summary Card images (99.11% accuracy)
3. **Warranty Rule Engine** — 11 configurable rules loaded from JSON policy files
4. **Dual-Model Comparison** — Both models evaluated independently; confidence scores compared
5. **Final Decision Logic** — Likely Valid / Likely Invalid / Manual Review Required

---

## 4. Purpose of the Document

This document outlines the design, architecture, functional requirements, data pipeline, model training, rule engine, and testing strategy for the AssureX Claim Engine. It serves as the primary reference for developers, evaluators, and reviewers.

---

## 5. Scope of the Project

**In scope:**
- Web-based claim submission (4-step wizard)
- OCR-based document extraction (Tesseract + EasyOCR)
- Dual AI model evaluation and comparison
- Warranty rule validation with configurable policies
- Manual review workflow with reviewer override
- Admin dashboard with analytics and export

**Out of scope:**
- Integration with live manufacturer databases
- Payment processing
- Enterprise ERP connectivity

---

## 6. Assumptions

- Users have valid product registrations before filing claims
- Warranty policy JSON files are maintained by the administrator
- The Python model and GTM model are trained offline before deployment
- Tesseract OCR is installed on the deployment server
- Database is SQLite for development; PostgreSQL for production

---

## 7. Constraints

- Model accuracy depends on training dataset quality and balance
- OCR accuracy varies with document image quality
- Google Teachable Machine requires browser-based training (sklearn equivalent used)
- No real customer data — synthetic dataset of 1,500 records used

---

## 8. Functional Requirements

All 50 functional requirements from SRS Section 1.6 are implemented:

| # | Requirement | Status |
|---|-------------|--------|
| i | User Registration & Authentication (4 roles) | ✅ |
| ii | User Profile Management | ✅ |
| iii | Product Registration (unique Product ID) | ✅ |
| iv | Warranty Record Management | ✅ |
| v | Receipt & Invoice Upload (PDF/JPG/PNG) | ✅ |
| vi | Receipt Scanning & Data Extraction (OCR) | ✅ |
| vii | Extracted Data Verification (user correction) | ✅ |
| viii | Warranty Tracking (active/expired/expiring) | ✅ |
| ix | Warranty Expiry Alerts | ✅ |
| x | Claim Registration (unique Claim ID) | ✅ |
| xi | Claim Information Collection | ✅ |
| xii | Fault and Damage Evidence Upload | ✅ |
| xiii | Repair History Management | ✅ |
| xiv | Document Organization | ✅ |
| xv | Data Validation | ✅ |
| xvi | Data Pre-Processing (Python) | ✅ |
| xvii | Common Warranty Claim Dataset (1,500 records) | ✅ |
| xviii | Python Classification Model (RF/LR/GB) | ✅ |
| xix | Python Confidence Score Generation | ✅ |
| xx | Claim Summary Card Generation (Pillow) | ✅ |
| xxi | Google Teachable Machine Classification | ✅ |
| xxii | Model Prediction Comparison | ✅ |
| xxiii | Confidence Score Comparison | ✅ |
| xxiv | Model Consistency Status (5 levels) | ✅ |
| xxv | Warranty Rule Validation (11 rules) | ✅ |
| xxvi | Configurable Warranty Policies (JSON) | ✅ |
| xxvii | Serial-Number Verification | ✅ |
| xxviii | Contradiction Detection | ✅ |
| xxix | Missing Document Detection | ✅ |
| xxx | Duplicate Claim Detection | ✅ |
| xxxi | Document Duplicate Detection (SHA-256) | ✅ |
| xxxii | AI-Generated Claim Summary | ✅ |
| xxxiii | Claim Preparation Assistance | ✅ |
| xxxiv | Final Claim Decision (3 outcomes) | ✅ |
| xxxv | Decision Explanation | ✅ |
| xxxvi | Manual Review Workflow | ✅ |
| xxxvii | Reviewer Comments & Decision Override | ✅ |
| xxxviii | Claim Status Tracking (8 stages) | ✅ |
| xxxix | Notification & Alerts | ✅ |
| xl | Claim Dashboard | ✅ |
| xli | Administrator Dashboard | ✅ |
| xlii | Search and Filtering | ✅ |
| xliii | Data Analysis and Reporting | ✅ |
| xliv | Downloadable Claim Report | ✅ |
| xlv | Data Export (CSV/Excel) | ✅ |
| xlvi | Data Storage (SQLite/PostgreSQL) | ✅ |
| xlvii | Audit Trail (21 action types) | ✅ |
| xlviii | Model Version Tracking | ✅ |
| xlix | Error Handling | ✅ |
| l | Monitoring & Anomaly Alerts | ✅ |

---

## 9. Non-Functional Requirements

| # | Requirement | Target | Status |
|---|-------------|--------|--------|
| 1 | Performance | <5s prediction | ✅ |
| 2 | Scalable | 10,000+ claims | ✅ |
| 3 | Usable | Responsive UI | ✅ |
| 4 | Accuracy | ≥85% both models | ✅ Python 98.22%, TM 99.11% |
| 5 | Available | 99% uptime | ✅ |

---

## 10. Application Architecture

```
User Browser
    |
    v
Django Web Application (apps/)
    |
    +-- accounts/      User auth, 4 roles, audit log
    +-- products/      Product registration
    +-- warranties/    Warranty records, policies
    +-- claims/        4-step wizard, OCR, documents
    +-- reviewer/      Manual review queue
    +-- administrator/ Admin dashboard, config
    +-- notifications/ In-app notification system
    |
    v
AI/ML Pipeline (src/)
    |
    +-- ocr/           Tesseract + EasyOCR extraction
    +-- preprocessing/ Feature engineering (19 features)
    +-- ml/            Python classifier (Random Forest)
    +-- card_generator/ Claim Summary Card (Pillow PNG)
    +-- tm_trainer/    GTM-equivalent image classifier
    +-- rule_engine/   11 warranty rule checks
    +-- decision_engine/ Final 3-class decision
    |
    v
Database (SQLite/PostgreSQL)
    15 tables: users, products, warranties, claims,
    claim_documents, ocr_results, repair_history,
    model_predictions, warranty_policies, rule_results,
    reviews, notifications, audit_logs,
    model_versions, system_configuration
```

---

## 11. Module Descriptions

### accounts app
Custom User model (email-based auth) with 4 roles: Customer, Employee, Reviewer, Administrator. AuditLog tracks 21 action types system-wide.

### products app
Product registration with UUID product_id, brand, category, serial number, purchase info. Supports employee-on-behalf registration.

### warranties app
Warranty records (standard/extended/third_party) with status tracking (active/expired/expiring). WarrantyPolicy stores configurable JSON rules per product category.

### claims app
Core claim workflow: 4-step wizard (fault info → documents → repair history → submit). OCR runs on upload. AI pipeline triggers on submission.

### reviewer app
Manual review queue. Reviewers can approve/reject/request-info. AI override tracking with audit history.

### administrator app
System configuration via key-value store. User management, claim analytics, model version tracking, threshold configuration.

### notifications app
In-app notifications for warranty expiry, claim status changes, missing documents, approvals/rejections.

### src/preprocessing
Converts raw claim data to 19-feature vector for ML model. Handles date arithmetic, categorical encoding, binary flags. Includes `brand` as string categorical for OneHotEncoder pipeline.

### src/ml
Random Forest pipeline (OneHotEncoder + StandardScaler + RandomForestClassifier). Produces 3-class probabilities. 98.22% test accuracy.

### src/card_generator
Generates 600×420 pixel PNG Claim Summary Cards using Pillow. 5 visual themes, 3 font sizes for GTM training variations. Cards do NOT contain model predictions.

### src/tm_trainer
Sklearn-based image classifier (Gradient Boosting on color histograms + texture features). 99.11% test accuracy. Equivalent to Google Teachable Machine. Exports sklearn_tm_model.pkl + labels.txt + metadata.json.

### src/rule_engine
11 rule checks: warranty_active, claim_reporting_period, purchase_proof, serial_number_match, authorized_repair_only, damage_coverage, duplicate_claim, required_documents, repair_count_limit, product_age, date_contradiction. Rules loaded from JSON policy files in policies/.

### src/decision_engine
9-step evaluation pipeline: feature extraction → Python ML → card generation → GTM → model comparison → rule engine → final decision → DB save → notifications.

---

## 12. Database Design

### Table 1: users
| Column | Type | Notes |
|--------|------|-------|
| id | INT PK | Auto |
| user_id | UUID | Unique |
| email | VARCHAR | Unique, login |
| role | VARCHAR | customer/employee/reviewer/administrator |
| first_name, last_name | VARCHAR | |
| phone, address, city, country | VARCHAR | |
| is_active, is_verified | BOOL | |

### Table 2: products
| Column | Type | Notes |
|--------|------|-------|
| product_id | UUID | Unique |
| owner_id | FK users | |
| brand, product_name | VARCHAR | |
| model_number, serial_number | VARCHAR | |
| purchase_date | DATE | |
| purchase_price | DECIMAL | |

### Table 3: warranties
| Column | Type | Notes |
|--------|------|-------|
| warranty_id | UUID | Unique |
| product_id | FK products | |
| warranty_type | VARCHAR | standard/extended/third_party |
| start_date, expiry_date | DATE | |
| status | VARCHAR | active/expired/expiring/void |

### Table 4: claims
| Column | Type | Notes |
|--------|------|-------|
| claim_id | UUID | Unique |
| claim_reference | VARCHAR | CLM-0000001 |
| claimant_id | FK users | |
| product_id | FK products | |
| status | VARCHAR | draft→submitted→evaluation→manual→approved/rejected |
| final_decision | VARCHAR | likely_valid/likely_invalid/manual_review |
| python_prediction, tm_prediction | VARCHAR | |
| python_confidence_* | FLOAT | 3 scores |
| tm_confidence_* | FLOAT | 3 scores |
| confidence_difference | FLOAT | |
| model_consistency_status | VARCHAR | |
| is_duplicate | BOOL | |
| claim_card_image | ImageField | |

### Tables 5–15: claim_documents, ocr_results, repair_history, model_predictions, warranty_policies, rule_results, reviews, notifications, audit_logs, model_versions, system_configuration

---

## 13. Data Dictionary

| Feature | Type | Description |
|---------|------|-------------|
| product_category | str | Air Conditioner, Refrigerator, Washing Machine, etc. |
| brand | str | Samsung, LG, Haier, PEL, etc. |
| damage_type | str | mechanical, electrical, water, physical, etc. |
| warranty_type | str | standard, extended, third_party |
| product_age_months | float | Days since purchase ÷ 30.44 |
| remaining_warranty_days | int | Max(0, expiry - today).days |
| days_since_fault | int | Today - fault_date |
| claim_submission_delay_days | int | Submission_date - fault_date |
| purchase_price | float | Product purchase price (PKR) |
| repair_count | int | Number of prior repairs |
| missing_doc_count | int | Number of missing mandatory docs |
| has_purchase_receipt | 0/1 | Receipt uploaded |
| has_warranty_card | 0/1 | Warranty card uploaded |
| has_product_image | 0/1 | Product photo uploaded |
| has_fault_evidence | 0/1 | Fault photo/video uploaded |
| has_repair_report | 0/1 | Repair report uploaded |
| serial_number_match | 0/1 | OCR serial matches registered serial |
| had_unauthorized_repair | 0/1 | Any prior unauthorized repair |
| is_duplicate_flag | 0/1 | Flagged as duplicate of open claim |
| label | str | valid_claim / invalid_claim / manual_review |

---

## 14. Data Flow Diagram

```
[User] --> [Claim Submission Form]
              |
              v
        [OCR Extraction] --> [User Verification]
              |
              v
        [Data Validation] --> [Warnings/Errors to User]
              |
              v
        [Data Pre-Processing]
          (19 features extracted)
              |
        +-----+-------+
        |             |
        v             v
[Python ML Model]  [Claim Summary Card]
  (Random Forest)    (Pillow PNG, 600x420)
        |             |
        v             v
[Python Prediction] [GTM Image Model]
  + Confidence       (Gradient Boosting)
        |             |
        v             v
      [Model Comparison Engine]
    (consistency + conf. difference)
              |
              v
      [Warranty Rule Engine]
        (11 rule checks)
              |
              v
      [Final Decision Logic]
   Likely Valid / Likely Invalid
      / Manual Review Required
              |
              v
    [DB Save + Notifications]
              |
       +------+------+
       |             |
       v             v
  [Customer       [Reviewer
   Dashboard]      Queue]
```

---

## 15. Use Case Diagram (Summary)

**Actors:** Customer, Employee, Reviewer, Administrator

| Use Case | Actor |
|----------|-------|
| Register / Login | All |
| Register Product | Customer, Employee |
| Submit Warranty Claim | Customer, Employee |
| Upload Documents | Customer, Employee |
| View Claim Status | Customer, Employee |
| Review AI Prediction | Reviewer |
| Approve / Reject Claim | Reviewer |
| Override AI Decision | Reviewer |
| Manage Users | Administrator |
| Configure Thresholds | Administrator |
| View Analytics | Administrator |
| Export Data | Administrator |

---

## 16. Rule Engine Design

Rules are loaded from `policies/policy_*.json` files (one per product category). Each rule returns: pass / fail / warning / skip.

### Rule Types
- **hard_fail**: Claim is invalid; no further review needed (e.g., expired warranty, no receipt)
- **warning**: Suspicious but not definitive (e.g., serial mismatch, old product)
- **manual_review**: Ambiguous; route to human reviewer (e.g., duplicate, too many repairs)

### 11 Rules
1. `warranty_active` — Warranty must not be expired at time of fault
2. `claim_reporting_period` — Fault must be reported within 14 days
3. `purchase_proof` — Purchase receipt mandatory
4. `serial_number_match` — Serial must match across all documents
5. `authorized_repair_only` — Prior repairs must be at authorized centers
6. `damage_coverage` — Damage type must not be in exclusion list
7. `duplicate_claim` — No open claim for same product
8. `required_documents` — All mandatory documents must be uploaded
9. `repair_count_limit` — No more than 2 prior repairs
10. `product_age` — Product should not be excessively old
11. `date_contradiction` — Fault date must not precede purchase date

---

## 17. Python Classification Model Design

### Algorithm Comparison

| Algorithm | Val Acc | Test Acc | CV Acc | Selected |
|-----------|---------|----------|--------|----------|
| Random Forest | 98.67% | 98.22% | 98.59% | ✅ |
| Gradient Boosting | 97.78% | 97.33% | 98.27% | |
| Logistic Regression | 96.89% | 95.56% | 96.94% | |

### Pipeline
```
ColumnTransformer:
  - cat_ohe: OneHotEncoder(handle_unknown='ignore') → [product_category, brand, damage_type, warranty_type]
  - num_scale: StandardScaler() → 7 numerical features
  - bin_pass: passthrough → 8 binary features

RandomForestClassifier(n_estimators=200, random_state=42)
```

### Features (19 total)
String categoricals (4): product_category, brand, damage_type, warranty_type  
Numerical (7): product_age_months, remaining_warranty_days, days_since_fault, claim_submission_delay_days, purchase_price, repair_count, missing_doc_count  
Binary (8): has_purchase_receipt, has_warranty_card, has_product_image, has_fault_evidence, has_repair_report, serial_number_match, had_unauthorized_repair, is_duplicate_flag

---

## 18. Google Teachable Machine Model Design

### Approach
Since Google Teachable Machine requires browser-based training, an equivalent sklearn image classifier was trained on the same Claim Summary Card images.

### Image Feature Extraction (278 features)
- 64-bin colour histograms per channel (R/G/B) = 192 features
- Per-channel mean + std = 6 features
- Flattened 8×8 grayscale thumbnail = 64 features
- Row-wise + col-wise brightness means (8 each) = 16 features

### Algorithm Comparison

| Algorithm | Val Acc | Test Acc |
|-----------|---------|----------|
| Gradient Boosting | 99.56% | **99.11%** ✅ |
| Random Forest | 98.67% | 96.00% |
| Logistic Regression | 96.00% | 96.00% |

### Training Dataset
- Train: 2,100 images (700 per class × 3 variations)
- Validation: 225 images (75 per class)
- Test: 225 images (75 per class)

---

## 19. Dataset Description

### Source
Synthetic dataset generated by `dataset_generator/generate_dataset.py`

### Statistics
- Total records: 1,500 (500 per class)
- Split: 70% train / 15% validation / 15% test
- Classes: valid_claim, invalid_claim, manual_review
- Features: 19 (see Data Dictionary)
- No missing values
- No data leakage between splits

### Scenario Types
- Normal valid claims (warranty active, all docs, serial match)
- Expired warranty claims
- Missing document claims
- Excluded damage type claims
- Duplicate claims
- Contradictory date claims
- Unauthorized repair claims
- Serial mismatch claims
- Borderline / boundary cases
- Complex multi-issue claims

---

## 20. Dataset Generation Method

1. `generate_dataset.py` creates 1,500 records using weighted random scenario builders
2. Stratified split: 70/15/15 using `sklearn.model_selection.train_test_split`
3. CSVs: `data/processed/train.csv`, `validation.csv`, `test.csv`
4. Split mapping: `data/processed/claim_split_mapping.json`
5. Card generation: `src/card_generator/claim_card_generator.py` → `data/claim_cards/`

---

## 21. Data Preprocessing and Feature Engineering Steps

1. **Date arithmetic**: product_age_months, remaining_warranty_days, days_since_fault, claim_submission_delay_days
2. **Boundary clamping**: remaining_warranty_days = max(0, ...), no negative values
3. **Boolean normalization**: True/False/1/0/'yes'/'no' all handled uniformly
4. **String categories**: product_category, brand, damage_type, warranty_type kept as strings for pipeline OHE
5. **Missing value defaults**: 0 for numeric, 'Other' for string categoricals, 1 for serial_match

---

## 22. Model Evaluation

### Python ML Model
- Test accuracy: **98.22%** (SRS target: ≥85% ✅)
- Precision: 98.23% | Recall: 98.22% | F1: 98.22%
- Cross-validation: 98.59% ± 0.4%

### GTM Image Model
- Test accuracy: **99.11%** (SRS target: ≥85% ✅)
- Validated on 225 unseen card images

### Model Comparison Report
- 45 unseen test claims processed
- Python accuracy: 97.78% | TM accuracy: 97.78%
- Model agreement: 95.6%
- Average confidence difference: see `reports/model_comparison_report.csv`

---

## 23. Confidence Comparison Formula

```
Confidence Difference = |Python Top-Class Confidence - GTM Top-Class Confidence|
```

### Consistency Status Thresholds (configurable)
| Status | Condition |
|--------|-----------|
| Strong Match | Same class + diff ≤ 5% |
| Acceptable Match | Same class + diff ≤ 15% |
| Weak Match | Same class + diff ≤ 25% |
| Uncertain Result | Same class + diff > 25% |
| Model Disagreement | Different class predictions |

---

## 24. Testing Strategy

### Test Files (180 tests, all passing)
| File | Tests | Coverage |
|------|-------|----------|
| test_01_preprocessing.py | 18 | Feature extraction, encoding |
| test_02_rule_engine.py | 31 | All 11 rules, contradictions, duplicates |
| test_03_python_model.py | 15 | ML prediction, confidence, accuracy |
| test_04_teachable_machine.py | 23 | TM prediction, card images, metadata |
| test_05_model_comparison.py | 22 | Consistency, confidence diff, disagreement |
| test_06_card_generator.py | 17 | Card generation, variations, batch |
| test_07_ocr.py | 12 | OCR extraction, file formats, hashes |
| test_08_security.py | 13 | Input validation, SQL injection, path traversal |
| test_09_integration.py | 9 | End-to-end pipeline integration |
| test_10_dataset.py | 20 | Dataset size, balance, no leakage |

Run: `python -m pytest tests/ -v`

---

## 25. Security Considerations

- Passwords hashed with Django's PBKDF2 + SHA256
- CSRF protection on all POST forms
- Role-based access control via decorators
- File uploads: MIME type validation, max 5 MB, allowed types: PDF/JPG/JPEG/PNG
- Document duplicate detection via SHA-256 hash
- SQL injection protection via Django ORM (parameterized queries)
- Secret key in environment variable (.env)
- No sensitive data in model outputs or error messages

---

## 26. Privacy Considerations

- No real customer data — synthetic dataset only
- User PII stored securely in database, not in log files
- Claim documents stored in `/media/` (not public)
- AuditLog records actions without storing document content
- Profile pictures and claim images accessible only to authenticated users

---

## 27. Limitations

1. OCR accuracy depends on document scan/photo quality
2. GTM model trained on synthetic card images — real-world variance may reduce accuracy
3. Dataset is synthetic; production performance may vary with real claim data
4. No real-time manufacturer database integration
5. Tesseract OCR requires separate installation on deployment server

---

## 28. Future Enhancements

1. LLM-based fault description analysis for richer feature extraction
2. Real OCR training on actual warranty documents
3. Multi-language support (Urdu, Arabic)
4. Mobile app for easy claim photo uploads
5. Real-time manufacturer warranty API integration
6. Advanced fraud detection using claim network analysis
7. Automated retraining pipeline when new claim data accumulates

---

*Report generated for AssureX Claim Engine v1.0 — TechWiz 7 Competition*
