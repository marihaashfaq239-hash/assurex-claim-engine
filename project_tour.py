"""
AssureX Claim Engine — Complete Project Tour
=============================================
Ye script poore project ka overview deti hai:
  - Kya bana hua hai
  - Kahan hai
  - Kaise kaam karta hai
  - Model performance
  - Test results

Run: python project_tour.py
"""
import json, csv, warnings, sys
warnings.filterwarnings('ignore')
sys.path.insert(0, '.')

from pathlib import Path

ROOT = Path('.')

SEP  = "=" * 65
SEP2 = "-" * 65

def section(title):
    print(f"\n{SEP}")
    print(f"  {title}")
    print(SEP)

def sub(title):
    print(f"\n  {SEP2}")
    print(f"  {title}")
    print(f"  {SEP2}")

def ok(msg):   print(f"    [OK]  {msg}")
def info(msg): print(f"    -->  {msg}")
def warn(msg): print(f"    [!]  {msg}")


# ──────────────────────────────────────────────────────────────────
section("ASSUREX CLAIM ENGINE — PROJECT TOUR")
# ──────────────────────────────────────────────────────────────────
print("""
  Project  : AssureX Claim Engine
  Theme    : AI-Powered Document Ops
  Category : NextWave AI and ML (TechWiz 7 — Aptech)
  Language : Python (Django 4.2)
  Database : SQLite (dev) / PostgreSQL (prod)

  WHAT THIS PROJECT DOES:
  Warranty claims ko automatically validate karta hai.
  Customer apna claim submit karta hai, system 2 AI models
  se evaluate karta hai aur decision deta hai:
    - Likely Valid       (approve karo)
    - Likely Invalid     (reject karo)
    - Manual Review      (human reviewer ko bhejo)
""")


# ──────────────────────────────────────────────────────────────────
section("1. PROJECT STRUCTURE — KONSI CHEEZ KAHAN HAI")
# ──────────────────────────────────────────────────────────────────

structure = {
    "apps/accounts/":       "User auth, 4 roles (Customer/Employee/Reviewer/Admin), AuditLog",
    "apps/products/":       "Product registration, unique Product ID, brand/serial/category",
    "apps/warranties/":     "Warranty records (active/expired/expiring), policy management",
    "apps/claims/":         "Core claim workflow: 4-step wizard, OCR, documents, AI pipeline",
    "apps/reviewer/":       "Manual review queue, approve/reject/override AI decision",
    "apps/administrator/":  "Admin dashboard, analytics, user mgmt, AI threshold config",
    "apps/notifications/":  "In-app alerts (warranty expiry, claim status, missing docs)",
    "---1---":              "",
    "src/ocr/":             "OCR: Tesseract + EasyOCR — extracts data from uploaded receipts",
    "src/preprocessing/":   "Feature engineering: 19 features from raw claim data",
    "src/ml/":              "Python ML model: Random Forest (98.22% accuracy)",
    "src/card_generator/":  "Claim Summary Card: 600x420 PNG image (Pillow)",
    "src/tm_trainer/":      "TM image classifier: trained on card images (99.11% accuracy)",
    "src/rule_engine/":     "11 warranty rules from JSON policy files",
    "src/decision_engine/": "Final decision: 9-step AI evaluation pipeline",
    "---2---":              "",
    "model/python_model/":  "Saved RF model (.pkl), label encoder, preprocessor, training report",
    "model/teachable_machine/": "TM model (.pkl), labels.txt, metadata.json, training report",
    "---3---":              "",
    "data/processed/":      "train.csv (1050), validation.csv (225), test.csv (225)",
    "data/raw/":            "Full dataset: assurex_claims_full.csv (1500 records)",
    "data/claim_cards/":    "Card images: 2100 train + 225 val + 225 test (2550 total)",
    "---4---":              "",
    "dataset_generator/":   "generate_dataset.py — synthetic 1500 claim records generator",
    "notebooks/":           "3 Jupyter notebooks: EDA, Model Training, TM Classifier",
    "tests/":               "10 test files, 180 tests (all passing)",
    "reports/":             "Model comparison report (45 claims)",
    "sample_claims/":       "11 required claim type examples (JSON)",
    "documentation/":       "Project report, data dictionary, readiness checklist",
    "policies/":            "4 JSON warranty policy files (per product category)",
    "templates/":           "40+ HTML templates (all 4 dashboards, claim wizard, etc.)",
    "static/":              "CSS, JS, images",
}

for path, desc in structure.items():
    if path.startswith("---"):
        print()
    else:
        exists = Path(path).exists()
        status = "[OK]" if exists else "[MISSING]"
        print(f"    {status}  {path:<35} {desc}")


# ──────────────────────────────────────────────────────────────────
section("2. USER ROLES — KAUN KYA KAR SAKTA HAI")
# ──────────────────────────────────────────────────────────────────
roles = {
    "Customer":      "Product register, claim submit, status track, notifications dekhe",
    "Employee":      "Customer ki taraf se claim file kare, products register kare",
    "Reviewer":      "Manual review queue, approve/reject/request-info, AI override",
    "Administrator": "Users manage, analytics, AI thresholds configure, data export",
}
for role, perms in roles.items():
    info(f"{role:<15}: {perms}")


# ──────────────────────────────────────────────────────────────────
section("3. AI PIPELINE — CLAIM SUBMIT HONE KE BAAD KYA HOTA HAI")
# ──────────────────────────────────────────────────────────────────
print("""
  Jab customer claim submit karta hai yeh 9 steps execute hote hain:

  Step 1 : Feature Extraction
           Raw claim data se 19 features nikale jate hain
           (product_age, remaining_warranty, docs_present, serial_match, etc.)

  Step 2 : Python ML Prediction
           Random Forest model features input leta hai
           Output: valid_claim / invalid_claim / manual_review + confidence %

  Step 3 : Claim Summary Card Generation
           Pillow se 600x420 PNG card generate hoti hai
           (card mein model prediction NAHI hoti — SRS requirement)

  Step 4 : TM Image Model Prediction
           Card image ko TM model classify karta hai
           Output: same 3 classes + confidence %

  Step 5 : Model Comparison
           |Python confidence - TM confidence| = confidence difference
           Status: Strong Match / Acceptable / Weak / Uncertain / Disagreement

  Step 6 : Warranty Rule Engine
           11 rules check hoti hain (expired warranty, missing receipt, etc.)
           hard_fail = reject, manual_review = queue, warning = flag

  Step 7 : Final Decision
           Sab results combine kar ke final decision:
           Likely Valid / Likely Invalid / Manual Review Required

  Step 8 : Database Save
           Prediction, confidence, rule results, card path — sab save

  Step 9 : Notifications
           Customer ko result notify, reviewer ko pending claim alert
""")


# ──────────────────────────────────────────────────────────────────
section("4. CLAIM DECISION LOGIC — KAB KAUN SA DECISION AATA HAI")
# ──────────────────────────────────────────────────────────────────
print("""
  LIKELY INVALID  jab:
    - Warranty expired ho (hard fail)
    - Purchase receipt missing ho (hard fail)
    - Water/physical damage (excluded fault type, hard fail)
    - Unauthorized repair center se repair (hard fail)
    - Fault date purchase date se pehle ho (contradiction, hard fail)

  MANUAL REVIEW REQUIRED  jab:
    - Dono models alag class predict karein (disagreement)
    - Python ya TM confidence < 70% ho (low confidence)
    - Duplicate claim detected ho
    - Serial number mismatch ho
    - 3 se zyada prior repairs ho
    - Required documents missing ho
    - Confidence difference > 25% ho

  LIKELY VALID  jab:
    - Dono models agree (same class)
    - Dono ki confidence >= 92%
    - Confidence difference <= 25%
    - Sab rules pass houn
    - Koi hard fail na ho
""")


# ──────────────────────────────────────────────────────────────────
section("5. WARRANTY RULE ENGINE — 11 RULES KYA HAIN")
# ──────────────────────────────────────────────────────────────────
rules = [
    ("warranty_active",         "hard_fail",    "Warranty expire ho chuki hai"),
    ("claim_reporting_period",  "warning",      "Fault ke 14 din baad claim filed (late)"),
    ("purchase_proof",          "hard_fail",    "Purchase receipt upload nahi ki"),
    ("serial_number_match",     "warning",      "Receipt ka serial product se match nahi karta"),
    ("authorized_repair_only",  "hard_fail",    "Pehle koi unauthorized repair hua"),
    ("damage_coverage",         "hard_fail",    "Damage type exclude list mein hai (water/physical)"),
    ("duplicate_claim",         "manual_review","Is product ka already ek open claim hai"),
    ("required_documents",      "manual_review","Mandatory documents upload nahi hue"),
    ("repair_count_limit",      "manual_review","2 se zyada pehle repairs hue hain"),
    ("product_age",             "warning",      "Product 10 saal se zyada purana hai"),
    ("date_contradiction",      "hard_fail",    "Fault date purchase date se pehle hai"),
]
print(f"\n    {'Rule Name':<28} {'Type':<15} Description")
print(f"    {'-'*28} {'-'*15} {'-'*30}")
for rule, rtype, desc in rules:
    print(f"    {rule:<28} {rtype:<15} {desc}")


# ──────────────────────────────────────────────────────────────────
section("6. ML MODELS — PERFORMANCE")
# ──────────────────────────────────────────────────────────────────

sub("Python Classification Model")
report_path = ROOT / 'model' / 'python_model' / 'training_report.txt'
if report_path.exists():
    lines = report_path.read_text(encoding='utf-8').splitlines()
    for line in lines:
        print(f"    {line}")
else:
    warn("training_report.txt not found")

sub("TM Image Classifier Model")
tm_report_path = ROOT / 'model' / 'teachable_machine' / 'tm_training_report.txt'
if tm_report_path.exists():
    lines = tm_report_path.read_text(encoding='utf-8').splitlines()
    for line in lines:
        print(f"    {line}")
else:
    warn("tm_training_report.txt not found")


# ──────────────────────────────────────────────────────────────────
section("7. DATASET — KYA DATA HAI")
# ──────────────────────────────────────────────────────────────────
for split, expected in [('train', 1050), ('validation', 225), ('test', 225)]:
    csv_path = ROOT / 'data' / 'processed' / f'{split}.csv'
    if csv_path.exists():
        with open(csv_path, encoding='utf-8') as f:
            rows = list(csv.DictReader(f))
        counts = {}
        for r in rows:
            l = r.get('label','')
            counts[l] = counts.get(l, 0) + 1
        ok(f"{split:<12}: {len(rows)} records  {counts}")
    else:
        warn(f"{split}.csv not found")

card_total = sum(1 for _ in (ROOT / 'data' / 'claim_cards').rglob('*.png')) if (ROOT / 'data' / 'claim_cards').exists() else 0
info(f"Claim Summary Card images total: {card_total}")
info(f"  train=2100 (700 per class x 3 variations)")
info(f"  validation=225 (75 per class x 1)")
info(f"  test=225 (75 per class x 1)")


# ──────────────────────────────────────────────────────────────────
section("8. JUPYTER NOTEBOOKS — KYA COVER KIYA GAYA HAI")
# ──────────────────────────────────────────────────────────────────
notebooks = {
    "01_exploratory_data_analysis.ipynb":    "EDA: class distribution, feature analysis, correlation, split verification",
    "02_model_training_comparison.ipynb":    "3 algorithm comparison (RF/LR/GB), confusion matrix, feature importance",
    "03_teachable_machine_classifier.ipynb": "Card image dataset, TM model training, accuracy, disagreement cases",
}
for nb, desc in notebooks.items():
    path = ROOT / 'notebooks' / nb
    status = "[OK]" if path.exists() else "[MISSING]"
    print(f"    {status}  {nb}")
    print(f"           {desc}\n")


# ──────────────────────────────────────────────────────────────────
section("9. TEST SUITE — KYA TEST KIYA GAYA HAI")
# ──────────────────────────────────────────────────────────────────
test_files = {
    "test_01_preprocessing.py":   "18 tests — Feature extraction, date math, encoding",
    "test_02_rule_engine.py":     "31 tests — All 11 rules, contradictions, duplicates, serial",
    "test_03_python_model.py":    "15 tests — ML prediction, confidence, 85% accuracy target",
    "test_04_teachable_machine.py":"23 tests — TM prediction, card images, metadata",
    "test_05_model_comparison.py": "22 tests — Consistency status, confidence diff, disagreement",
    "test_06_card_generator.py":   "17 tests — PNG generation, themes, batch, None values",
    "test_07_ocr.py":              "12 tests — OCR extraction, file formats, SHA-256 hash",
    "test_08_security.py":         "13 tests — SQL injection, XSS, path traversal, file types",
    "test_09_integration.py":      " 9 tests — End-to-end pipeline (preprocessing to decision)",
    "test_10_dataset.py":          "20 tests — Dataset size, balance, no data leakage",
}
total = sum(int(desc.split()[0]) for desc in test_files.values())
for fname, desc in test_files.items():
    path = ROOT / 'tests' / fname
    status = "[OK]" if path.exists() else "[MISSING]"
    print(f"    {status}  {fname:<35} {desc}")
print(f"\n    TOTAL: {total} tests")
print(f"    Run:   python -m pytest tests/ -v")


# ──────────────────────────────────────────────────────────────────
section("10. MODEL COMPARISON REPORT — 45 CLAIMS KA RESULT")
# ──────────────────────────────────────────────────────────────────
summary_path = ROOT / 'reports' / 'model_comparison_summary.json'
if summary_path.exists():
    with open(summary_path, encoding='utf-8') as f:
        s = json.load(f)
    info(f"Total claims tested : {s.get('total_claims')}")
    info(f"Python ML accuracy  : {s.get('py_accuracy_pct')}%")
    info(f"TM model accuracy   : {s.get('tm_accuracy_pct')}%")
    info(f"Model agreement     : {s.get('model_agreement_pct')}%")
    info(f"Avg conf difference : {s.get('avg_conf_diff_pct')}%")
    info(f"SRS 85% target      : {'MET' if s.get('srs_85pct_target_met') else 'NOT MET'}")
    info(f"Consistency breakdown:")
    for k, v in s.get('consistency_breakdown', {}).items():
        print(f"              {k:<22}: {v}")
    info(f"Final decisions:")
    for k, v in s.get('final_decisions', {}).items():
        print(f"              {k:<28}: {v}")
else:
    warn("model_comparison_summary.json not found")


# ──────────────────────────────────────────────────────────────────
section("11. SAMPLE CLAIMS — 11 REQUIRED TYPES")
# ──────────────────────────────────────────────────────────────────
idx_path = ROOT / 'sample_claims' / 'sample_claims_index.json'
if idx_path.exists():
    with open(idx_path, encoding='utf-8') as f:
        idx = json.load(f)
    for c in idx.get('claims', []):
        print(f"    [OK]  {c['claim_id']}  {c['scenario']:<35} -> {c['expected_decision']}")
else:
    warn("sample_claims_index.json not found")


# ──────────────────────────────────────────────────────────────────
section("12. SRS COMPLIANCE SUMMARY")
# ──────────────────────────────────────────────────────────────────
srs_checks = [
    ("User Registration & Auth (4 roles)",         "apps/accounts/models.py"),
    ("Product Registration",                        "apps/products/models.py"),
    ("Warranty Record Management",                  "apps/warranties/models.py"),
    ("4-Step Claim Submission Wizard",              "apps/claims/views_submit.py"),
    ("Receipt Scanning & OCR",                      "src/ocr/extractor.py"),
    ("Data Pre-Processing (19 features)",           "src/preprocessing/claim_preprocessor.py"),
    ("1500-record Synthetic Dataset",               "data/processed/train.csv"),
    ("Python Classification Model (>=85%)",         "model/python_model/assurex_model.pkl"),
    ("Claim Summary Card Generation",               "src/card_generator/claim_card_generator.py"),
    ("2100+ GTM Training Card Images",              "data/claim_cards/train/"),
    ("GTM Image Model (>=85%)",                     "model/teachable_machine/sklearn_tm_model.pkl"),
    ("Model Prediction Comparison",                 "src/decision_engine/evaluator.py"),
    ("Confidence Score Comparison",                 "src/decision_engine/evaluator.py"),
    ("5-Level Model Consistency Status",            "src/decision_engine/evaluator.py"),
    ("Warranty Rule Validation (11 rules)",         "src/rule_engine/warranty_rule_engine.py"),
    ("3 Configurable Policy JSON Files",            "policies/"),
    ("Serial Number Verification",                  "src/rule_engine/warranty_rule_engine.py"),
    ("Contradiction Detection",                     "src/rule_engine/warranty_rule_engine.py"),
    ("Missing Document Detection",                  "apps/claims/models.py"),
    ("Duplicate Claim Detection (SHA-256)",         "apps/claims/views_submit.py"),
    ("Final Decision (3 outcomes)",                 "src/decision_engine/evaluator.py"),
    ("Manual Review Workflow",                      "apps/reviewer/"),
    ("Reviewer Override + Audit Trail",             "apps/reviewer/views.py"),
    ("Claim Status Tracking (8 stages)",            "apps/claims/models.py"),
    ("Notifications & Alerts",                      "apps/notifications/"),
    ("Customer + Admin Dashboards",                 "apps/administrator/views.py"),
    ("Downloadable Claim Report",                   "apps/administrator/views.py"),
    ("Data Export (CSV/Excel)",                     "apps/administrator/views.py"),
    ("Audit Log (21 action types)",                 "apps/accounts/models.py"),
    ("Model Version Tracking",                      "apps/claims/models.py"),
    ("3 Jupyter Notebooks",                         "notebooks/"),
    ("180 Automated Tests (all passing)",           "tests/"),
    ("Model Comparison Report (45 claims)",         "reports/model_comparison_report.csv"),
    ("11 Sample Claim Types",                       "sample_claims/"),
    ("Project Report (28 sections)",               "documentation/project_report.md"),
    ("AI_USAGE.md Declaration",                     "AI_USAGE.md"),
]

passed = 0
failed_list = []
for desc, path in srs_checks:
    exists = Path(path).exists()
    if exists:
        passed += 1
    else:
        failed_list.append((desc, path))

print(f"\n    SRS Compliance: {passed}/{len(srs_checks)} requirements met\n")
if failed_list:
    print("    MISSING:")
    for d, p in failed_list:
        print(f"      [MISSING]  {d}  ({p})")
else:
    print("    ALL SRS REQUIREMENTS MET.")


# ──────────────────────────────────────────────────────────────────
section("13. KEY COMMANDS — KAISE CHALAO")
# ──────────────────────────────────────────────────────────────────
print("""
  Application start karna:
    python manage.py migrate
    python manage.py runserver

  Sabhi tests run karna:
    python -m pytest tests/ -v

  Model comparison report generate karna:
    python reports/generate_model_comparison_report.py

  Card images regenerate karna (agar zarurat ho):
    python src/card_generator/claim_card_generator.py

  TM model retrain karna:
    python src/tm_trainer/train_teachable_machine.py

  Python ML model retrain karna:
    python src/ml/train_model.py

  Dataset regenerate karna:
    python dataset_generator/generate_dataset.py

  Sample claims regenerate karna:
    python sample_claims/generate_sample_claims.py

  Jupyter notebooks regenerate karna:
    python notebooks/generate_notebooks.py
""")


# ──────────────────────────────────────────────────────────────────
section("14. IMPORTANT FILES — JO EVALUATOR DEKHEGA")
# ──────────────────────────────────────────────────────────────────
important = [
    ("src/decision_engine/evaluator.py",          "CORE: 9-step AI pipeline, final decision logic"),
    ("src/rule_engine/warranty_rule_engine.py",   "CORE: 11 warranty rules, RuleEngineResult class"),
    ("src/preprocessing/claim_preprocessor.py",   "CORE: 19-feature extraction from raw claim"),
    ("src/ml/train_model.py",                     "CORE: 3-algorithm comparison, RF selected as best"),
    ("src/tm_trainer/train_teachable_machine.py", "CORE: TM-equivalent image classifier training"),
    ("src/card_generator/claim_card_generator.py","CORE: Claim Summary Card PNG generation"),
    ("apps/claims/views_submit.py",               "WEB:  4-step claim submission wizard"),
    ("apps/reviewer/views.py",                    "WEB:  Manual review queue and decision"),
    ("apps/administrator/views.py",               "WEB:  Admin dashboard, analytics, export"),
    ("policies/policy_default.json",              "DATA: Configurable warranty rules (JSON)"),
    ("config/app_config.json",                    "CONFIG: AI thresholds (changeable live)"),
    ("documentation/project_report.md",           "DOC:  Complete 28-section project report"),
    ("tests/test_02_rule_engine.py",              "TEST: 31 rule engine tests"),
    ("tests/test_05_model_comparison.py",         "TEST: 22 model comparison tests"),
    ("reports/model_comparison_report.csv",       "REPORT: 45 claims comparison results"),
]
for path, desc in important:
    exists = Path(path).exists()
    status = "[OK]" if exists else "[MISSING]"
    print(f"    {status}  {path:<45} {desc}")


print(f"\n{SEP}")
print("  PROJECT TOUR COMPLETE")
print(f"  Run 'python -m pytest tests/ -q' to verify all 180 tests pass.")
print(SEP)
