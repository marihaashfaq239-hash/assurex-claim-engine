# AI Usage Declaration — AssureX Claim Engine

> **SRS Section 1.8 requirement:** Every AI tool used during development must be declared.
> This file covers what AI helped with, what we changed, and what we tested ourselves.

---

## Usage Breakdown

| Contributor | Contribution % | Details |
|---|---|---|
| **Team (Human)** | **70%** | Architecture decisions, ML training, dataset design, OCR regex, bug fixes, testing, deployment, UI theme, all JSON policies, all diagrams, documentation |
| **Kiro AI (AI Tool)** | **30%** | Code scaffolding, boilerplate, initial form/model structure, test boilerplate, template structure |

> The final claim decision is produced by our own trained Python ML model + GTM proxy + rule engine — **not** by any external AI API.

---

## Why We Used AI Tools

Honestly, this project has a lot of moving parts — Django backend, two ML models, OCR pipeline, warranty rule engine, 40+ templates. We used Kiro (an AI coding assistant in our IDE) to speed up repetitive code like model definitions, form widgets, and test boilerplate. But we didn't just copy-paste — we ran everything, broke things, fixed them, and made changes where the AI got it wrong (which happened more than a few times).

---

## Tool Used

**Kiro AI** — AI coding assistant inside the Kiro IDE (Amazon)

We did NOT use ChatGPT, GitHub Copilot, or any external API to make claim decisions. The AI pipeline in this project runs our own trained models — not any generative AI.

---

## What Kiro Helped With (and What We Changed)

### Django Backend

**accounts app**
Kiro wrote the initial CustomUser model and LoginForm. We had to fix the `get_initials()` method because it broke on users with only one name. We also added the `is_verified` flag ourselves after realizing it was missing. Tested all 4 roles manually — login, dashboard redirect, and 403 handling.

**products app**
Kiro generated the ProductRegistrationForm. The serial number field had no validation at first — we added the clean method ourselves after testing showed empty serial numbers were being accepted. Ran tests by registering actual products with edge case inputs.

**warranties app**
The initial warranty expiry calculation had a bug — it used 30 days per month flat which gave wrong dates for months like February. We fixed it to use proper `timedelta` math. Also added the manual warranty creation form (`WarrantyAddForm`) after realizing auto-creation only covered standard warranties.

**claims app — 4-step wizard**
This was the most complex part. Kiro helped scaffold the 4 views but the OCR integration was messy — field mappings were wrong for Pakistani receipt formats (date format, PKR currency). We spent a full day fixing the date parser regex. The `_detect_contradictions()` function has 23 checks — Kiro wrote about 15, we added 8 more specific ones after testing with real scenarios.

**reviewer app**
Kiro wrote the queue view and detail view. We added the AI override tracking ourselves — the original version didn't save `ai_original_result` to the Review model, we caught this during testing.

**administrator app**
Analytics charts data format was wrong initially — Chart.js expects specific JSON structure that Kiro got slightly off. We fixed the `json.dumps()` calls. The `avg_confidence` metric was hardcoded as `None` — we wrote the actual `Avg()` query ourselves.

**notifications app**
Basic structure from Kiro. We wrote the 12 notification type constants and the `Notification.send()` factory method ourselves after the initial version didn't handle duplicate notifications properly.

---

### ML/AI Pipeline (src/)

**OCR (src/ocr/extractor.py)**
Kiro wrote the basic Tesseract wrapper. The regex patterns for extracting invoice numbers and Pakistani price formats (with commas like "1,50,000") needed heavy manual work. We tested on 5 actual receipt photos and rewrote 3 of the 6 field parsers.

**Preprocessing (src/preprocessing/claim_preprocessor.py)**
Kiro wrote the initial feature extraction. Big problem — `brand` was not included as a feature even though the model needed it. We caught this when predictions were returning wrong classes on brand-specific claims. Fixed `ALL_FEATURES` list and `build_feature_dict()` ourselves. This took about 3 hours to debug.

**Python ML Model (src/ml/train_model.py)**
Kiro wrote the training script structure. We ran the training, compared 3 algorithms (Random Forest, Logistic Regression, Gradient Boosting), and Random Forest gave 98.22% on test set — above the 85% SRS target. We reviewed the confusion matrix and noticed the model was slightly weak on `manual_review` class boundary cases — acceptable for competition purpose.

**Claim Summary Card Generator (src/card_generator/claim_card_generator.py)**
Kiro wrote the initial version with Pillow. We had to verify that the card does NOT show Python prediction anywhere — SRS explicitly says this. Found one label was showing on card Theme 3, removed it. Generated all 2,550 images ourselves.

**Teachable Machine Trainer (src/tm_trainer/)**
Kiro wrote the sklearn-based image classifier as TM proxy. We trained it ourselves, got 99.11% accuracy. The labels.txt format was wrong initially — fixed to match evaluator.py expectations.

**Rule Engine (src/rule_engine/warranty_rule_engine.py)**
Kiro wrote 7 of the 11 rule functions. We wrote `check_unauthorized_repair`, `check_claim_reporting_period`, and `check_product_age_vs_warranty` ourselves after testing showed edge cases weren't covered. Also fixed `is_hard_fail` which was a method call `()` instead of a property — caused AttributeError in production.

**Decision Engine (src/decision_engine/evaluator.py)**
Kiro wrote the pipeline structure. We updated `run_teachable_machine()` to use the sklearn model as primary (not TF SavedModel which we didn't have). Tested full pipeline end-to-end with all 3 decision classes.

---

### Dataset

Kiro helped write `dataset_generator/generate_dataset.py` structure. We defined the 3 scenario types (valid, invalid, manual_review) ourselves based on SRS requirements. Ran the generator, verified 500 records per class, confirmed the 70/15/15 split is stratified. Checked that no claim ID appears in both train and test splits.

---

### Templates and Frontend

Kiro generated HTML structure for most templates. We:
- Changed the entire color theme from navy blue to forest green + butter yellow
- Added the landing page 3D particle background (vanilla Canvas 2D — no CDN)
- Fixed sidebar active link colors (had wrong hardcoded blue values)
- Added the product deactivate confirmation modal ourselves
- Made all forms responsive on mobile

---

### Tests

Kiro wrote test boilerplate. We ran all tests, and they didn't all pass initially:
- `test_02` had 3 failing tests due to the `is_hard_fail` property bug — we fixed both the source code and the tests
- `test_03` had wrong feature expectations after we added `brand` — fixed
- `test_09` integration tests failed because TM model wasn't loading — fixed by updating the sklearn fallback path

Final state: 180 tests, all passing.

---

## Things AI Got Wrong (We Fixed)

| Bug | Where | How We Found It | What We Did |
|-----|-------|-----------------|-------------|
| `brand` missing from features | preprocessing | Wrong predictions on branded products | Added `brand` to ALL_FEATURES, retrained |
| `is_hard_fail` was method not property | rule_engine | AttributeError in production | Changed to `@property` |
| Warranty expiry using 30 days/month flat | warranties | Feb dates were wrong | Fixed to proper timedelta |
| OCR date parser failed on Pakistani formats | OCR | Test receipts failed | Rewrote date regex |
| Card generator showing prediction label | card_generator | Manual inspection | Removed label from Theme 3 |
| avg_confidence hardcoded None | admin analytics | Metric always blank | Wrote Avg() query |
| Chart.js data format wrong | admin analytics | Charts not rendering | Fixed json.dumps structure |
| AI override not saving original result | reviewer | Missing audit entry | Added ai_original_result field save |

---

## What AI Did NOT Do

- Did not decide the dataset scenario logic — we defined what makes a claim valid/invalid/manual
- Did not train the models — we ran training scripts ourselves
- Did not write the warranty policy JSON files — we wrote those based on SRS requirements
- Did not verify model accuracy — we ran evaluation and checked confusion matrix
- Did not test the application — we manually tested every user flow

---

## Declaration

We understand every part of this project. The AI assistant helped us write faster, but we reviewed everything, broke things, fixed bugs, and made the final decisions on architecture and logic.

If an evaluator asks us to:
- Explain any function — we can
- Add a new warranty exclusion — open `policies/policy_*.json`, add to `exclusions` array
- Change confidence threshold — Admin panel → AI Thresholds → update value
- Add a new contradiction rule — `apps/claims/views_submit.py` → `_detect_contradictions()` function

We are ready for the surprise modification task.

**Team:** Hunain (and team)
**Submission Date:** September 2026
**AI Tool:** Kiro AI — Amazon Kiro IDE
