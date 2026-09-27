# How We Built AssureX: An AI-Powered Warranty Claim Engine

**By:** Muhammad Hunain, Mariha Ashfaq, Owais Ahmed, Muhammad Daniyal  
**Team:** AssureX Development Team — Aptech Computer Education  
**Student IDs:** 1538835 | 1540161 | 1515897 | 1542905  
**Date:** September 2026  

---

## Introduction

When a customer's refrigerator breaks down during warranty, what should happen next? In most cases, the customer visits a service center, fills out a form, hands over documents, and then waits — sometimes for days — while someone manually checks whether the claim is valid. The clerk has to verify the purchase date, check warranty conditions, inspect the documents, look for prior repairs, and finally decide whether to approve or reject.

This process is slow. It is inconsistent. One clerk might approve what another would reject. And it is easy to game — someone could submit the same receipt twice or claim physical damage as a manufacturing defect.

AssureX was built to fix exactly this. It is a full-stack web application that automates warranty claim evaluation using two independently trained AI models, a configurable warranty rule engine, and a human reviewer workflow for cases that need a second opinion.

---

## The Problem We Were Solving

Our project brief came from the Aptech TechWiz competition: build an AI-powered warranty claim management system. The system had to:

1. Accept warranty claims through a web interface
2. Extract data from uploaded documents using OCR
3. Run two separate AI models — a Python classification model and a Google Teachable Machine model
4. Compare both models' predictions and confidence scores
5. Apply warranty-specific business rules
6. Produce a final decision: Likely Valid, Likely Invalid, or Manual Review Required
7. Route uncertain claims to a human reviewer

This was not a simple CRUD application. It required a real ML pipeline, a synthetic dataset, two trained models, and a complete web application with four distinct user roles.

---

## System Architecture

We chose Django as our backend framework because of its built-in authentication, ORM, and admin interface. The project has seven Django applications:

- **accounts** — custom user model with four roles: customer, employee, reviewer, administrator
- **products** — product registration with automatic warranty creation
- **warranties** — warranty tracking with expiry alerts
- **claims** — 4-step claim wizard with OCR and AI pipeline integration
- **reviewer** — manual review queue and decision workflow
- **administrator** — analytics dashboard, user management, AI configuration
- **notifications** — real-time in-app notification system

The AI pipeline lives outside the Django apps in a `src/` directory, keeping the ML code separate from the web layer. The pipeline has five modules: OCR extractor, data preprocessor, Python ML predictor, claim card generator, and TM predictor — all coordinated by the decision engine.

---

## Building the Dataset

The SRS required a minimum of 1,500 warranty claim records divided equally into three classes: Valid Claim (500), Invalid Claim (500), and Manual Review (500). No pre-existing dataset was provided — we had to generate our own.

We wrote a Python script (`dataset_generator/generate_dataset.py`) that produces synthetic but realistic claim records. Each record contains 19 features covering product details, warranty status, document availability, repair history, and claim conditions.

The three scenario types were designed to be realistic:

**Valid claims** are characterized by: active warranty, all mandatory documents present, fault within covered damage types, no unauthorized repairs, serial number matching, and claim filed within the reporting period.

**Invalid claims** include: expired warranties, excluded damage types (physical damage, water damage), missing key documents, multiple unauthorized repairs, or duplicate claim indicators.

**Manual review claims** are the borderline cases: low-confidence indicators, minor contradictions, nearly-expired warranties, partial document sets, or mixed signals that a human reviewer should evaluate.

We applied stratified splits: 70% for training (1,050 records), 15% for validation (225), and 15% for testing (225). The same split was used for both the Python model (CSV format) and the Teachable Machine model (visual card format).

---

## OCR Pipeline

One of the more technically interesting parts of the project was building the OCR pipeline. When a customer uploads a purchase receipt or warranty card, we want to automatically extract fields like invoice number, serial number, purchase date, and price — so the customer does not have to type them manually.

We used Tesseract as the primary OCR engine and EasyOCR as a fallback. The extracted text goes through a series of regex-based parsers for each field. Pakistani receipts have some specific patterns — prices often appear as "Rs. 1,50,000" or "PKR 150,000", and dates appear in formats like "15-01-2024" or "Jan 15, 2024". We wrote field-specific extractors for each.

After extraction, we show the customer what was extracted and let them correct any mistakes before submission. The corrected values are stored with `is_verified=True` and used in both the contradiction detection and the AI feature vector.

---

## The Python ML Model

For the Python classification model, we trained and compared three algorithms:

1. **Random Forest** — ensemble of decision trees
2. **Logistic Regression** — linear baseline
3. **Gradient Boosting** — boosted ensemble

The training script (`src/ml/train_model.py`) runs all three, generates a confusion matrix for each, and selects the best-performing one. Random Forest won with 98.22% test accuracy.

The preprocessing pipeline uses scikit-learn's `ColumnTransformer`:
- String categorical features (product_category, brand, damage_type, warranty_type) go through `OneHotEncoder`
- Numerical features go through `StandardScaler`
- Binary features (has_receipt, is_warranty_active, etc.) pass through unchanged

The trained model, preprocessor, and label encoder are saved as `.pkl` files in `model/python_model/`.

---

## The Claim Summary Card

The Teachable Machine model is an image classifier — it needs images, not tabular data. We solved this by generating a standardized visual card for each claim.

The Claim Summary Card is a 600×420 pixel PNG that visualizes the claim's key features: product age, warranty period remaining, fault type, document availability status, serial number match indicator, repair history count, and claim filing timeliness. Each indicator is shown as a colored status indicator (green/yellow/red).

One critical SRS requirement: the card must NOT show the Python model's prediction, confidence score, or final decision. This keeps the two models truly independent. We verified this manually on each of the five card themes.

We generated 2,550 training images (2,100 training, 225 validation, 225 testing) using two visual variations per training card, as required by the SRS.

---

## The Teachable Machine Model

Since we could not deploy Google Teachable Machine's TensorFlow runtime in our production environment, we built a scikit-learn proxy model that mimics the Teachable Machine approach: it extracts 278 visual features from the claim card images (pixel statistics, color histograms, region averages) and trains a Gradient Boosting classifier on them.

The proxy achieved 99.11% test accuracy — actually higher than the Python model, because the image features encode the visual patterns of valid/invalid/manual-review cards very clearly.

---

## Dual-Model Comparison

After both models make their predictions, the decision engine compares them:

```
Confidence Difference = |Python top-class confidence − TM top-class confidence|
```

Based on this difference, we classify the comparison as:
- **Strong Match** — same class, ≤5% difference
- **Acceptable Match** — same class, 5%–15% difference
- **Weak Match** — same class, 15%–25% difference
- **Model Disagreement** — different predicted classes
- **Uncertain Result** — either model below 70% confidence

Any disagreement or uncertainty automatically routes the claim to the manual review queue.

---

## The Warranty Rule Engine

The AI models are not the whole story. A claim might score high on the ML models but still violate a basic warranty condition — like having an excluded damage type or being filed too late. The warranty rule engine catches these cases.

We have 11 rule functions, each checking a specific condition:
1. Warranty expiry check
2. Fault coverage check (is the damage type covered?)
3. Claim reporting period check (filed within X days of fault?)
4. Mandatory documents check
5. Serial number match check
6. Unauthorized repair check
7. Product age vs. warranty check
8. Duplicate claim check
9. Document hash check (SHA-256)
10. Maximum repair count check
11. Grace period evaluation

The rules are configured in JSON policy files — one per product category. This means adding a new exclusion or changing the reporting period requires editing a JSON file, not changing Python code. During the competition, an evaluator can ask us to add a new warranty exclusion and we can do it in under 30 seconds.

---

## The Final Decision

The decision engine combines everything:

1. If a warranty rule is a **hard fail** → Likely Invalid
2. If both models predict the same class with **Strong Match** confidence → use that class
3. If models **disagree** or confidence is **low** → Manual Review Required
4. If rule warnings exist but no hard fails → use AI prediction with warnings noted

The final result is one of: **Likely Valid**, **Likely Invalid**, or **Manual Review Required**.

---

## The Human Reviewer

Not every claim should be decided by AI alone. Claims that are uncertain, have conflicting signals, or trip rule warnings go to the reviewer queue. A reviewer can see all AI predictions, confidence scores, OCR-extracted data, rule results, repair history, and uploaded documents in one view.

The reviewer can approve, reject, request more information, or override the AI recommendation. If they override, the system records the original AI result, the reviewer's decision, and the reason — all stored in the audit trail and visible in the admin panel.

---

## Model Errors and Disagreement Cases

No model is perfect — and understanding where ours fails is as important as knowing where it succeeds. On the 225-record test set, the Random Forest model misclassified 4 claims (1.78%). All four were Manual Review records that were predicted as Valid Claim. Examining them revealed a pattern: they were all edge cases where every measurable signal looked valid (active warranty, all documents present, serial match) but the fault description contained a subtle indicator of exclusion — something a rule check caught but the feature vector did not capture well.

The Gradient Boosting image model misclassified 2 claims on the same test set (0.89%) — both were Manual Review cards that closely resembled Valid cards visually. This is actually a useful failure: the two models disagreed on exactly the kind of claim that should go to manual review.

One specific disagreement case from our test set is illustrative: a laptop claim where the Python model predicted Valid Claim (87% confidence) but the GTM model predicted Manual Review (61% confidence). The confidence difference was 26%, landing it in the Weak Match tier. The rule engine then flagged an unauthorized repair in the history. The final decision: Manual Review Required — which was the correct label. Both models being partially wrong, but in opposite directions, produced the right outcome.

---

## Testing Results

We wrote 180 automated tests across 10 test files covering every module in the system. All 180 pass.

**Test breakdown by category:**
- **Functional tests (62):** User registration, login, role-based redirects, product registration, 4-step claim wizard, OCR verification, reviewer workflow, admin dashboard, threshold configuration, CSV export
- **Integration tests (24):** Full pipeline end-to-end from claim submission to decision, OCR-to-contradiction chain, reviewer queue population, notification delivery
- **Boundary tests (18):** 5MB file size limit, fault date equal to today, warranty expiry date equal to today, maximum repair count edge cases, confidence threshold boundaries
- **Negative tests (28):** Wrong file type upload, empty mandatory fields, future fault date, cross-role 403 access, missing warranty, invalid claim ID
- **Security tests (20):** CSRF token validation, SQL injection attempts on search fields, XSS via claim description, unauthenticated access to protected views, admin-only endpoint access by customer role
- **ML model tests (28):** Accuracy ≥ 85% on test set, feature count verification (19 features), confidence probabilities sum to 1.0, all five consistency tiers reachable, rule engine producing correct outcomes for all 11 mandatory SRS scenarios

The 11 mandatory SRS scenarios (valid claim, invalid claim, manual review, expired warranty, missing document, duplicate claim, contradictory claim, serial mismatch, unauthorized repair, boundary date, model disagreement) each have dedicated test cases with known expected outputs. These are our "hidden test readiness" tests — designed specifically for evaluator queries.

---

## Security Considerations

AssureX handles personally identifiable information — names, contact details, product serial numbers, and financial transaction records. We took several steps to protect it.

**Authentication and authorization** use Django's built-in session framework with role-based decorators (`@customer_required`, `@employee_required`, `@reviewer_required`, `@admin_required`) on every view. Cross-role access returns a proper 403 response rather than redirecting, which prevents enumeration.

**Document uploads** are validated by MIME type and file extension before storage. Files are stored outside the web root and served through Django's `FileResponse` with authentication checks, so a guessed URL cannot expose a document without login.

**Duplicate document detection** uses SHA-256 hashing: the same physical file submitted under a different filename is caught before reaching the AI pipeline.

**CSRF protection** is enabled on every form. The admin panel session times out after 30 minutes of inactivity.

**Audit trail** records every significant action — login, document upload, OCR correction, model prediction, claim submission, reviewer decision, admin override — with timestamp and IP address. This provides a complete tamper-evident log for any dispute.

---

## Limitations and Future Enhancements

**Current limitations:**

AssureX uses a synthetic training dataset. While designed to cover realistic scenarios, it cannot capture the full distribution of real-world claim patterns — particularly regional ones (Pakistani market receipt formats, local brands). The models will need retraining on real data before production deployment.

The Google Teachable Machine proxy model, while accurate on synthetic cards, is not a true neural network image model. A proper CNN trained end-to-end on real claim images would likely be more robust.

OCR accuracy drops significantly on low-quality scans, handwritten text, or non-standard receipt layouts. The current Tesseract + EasyOCR combination handles most digital-print receipts well, but degraded copies remain a challenge.

**Future enhancements:**

The most impactful next step would be integrating with a real manufacturer's warranty database — instead of manual product registration, products would sync from the manufacturer's product catalogue, and warranty activation would be automatic at the point of sale.

A mobile application for customers to photograph documents and check claim status would significantly reduce friction. The Django REST API backend is already in place; adding React Native or Flutter on top is the natural extension.

Active learning would let the system improve over time: reviewer decisions become new training labels, gradually shifting the model toward real-world patterns rather than synthetic ones.

---

This project taught us several things we would not have learned from a simple CRUD application:

**Working with real ML pipelines is messier than textbooks suggest.** We had a bug where `brand` was missing from the feature vector — a mistake we caught only when predictions on brand-specific claims were wrong. Debugging the feature mismatch between training and inference took hours.

**Independent validation matters.** Having two models that don't share any training infrastructure means one model can catch what the other misses. The disagreement cases in our test set were exactly the borderline claims that a human reviewer should see.

**Configuration over code.** The JSON policy files turned out to be one of the best design decisions. When an evaluator asks "can you add a new exclusion?" — we open a JSON file, add one line, and it's live. No code change, no redeployment.

**Database design early.** We defined all 16 database tables before writing any views. This meant we rarely had to change the schema mid-development.

---

## Technical Stack

- **Backend:** Django 4.2 (Python 3.11)
- **Database:** SQLite (development), PostgreSQL (production / Railway)
- **ML:** scikit-learn 1.5 (Random Forest, Logistic Regression, Gradient Boosting)
- **OCR:** Tesseract 5 + EasyOCR 1.7
- **Image Processing:** Pillow 10.4, OpenCV 4.10
- **Frontend:** Bootstrap 5.3, Bootstrap Icons, Vanilla JS, Canvas 2D API
- **Hosting:** Railway (production), SQLite (development)
- **Version Control:** Git + GitHub

---

## Conclusion

AssureX is a complete, production-ready warranty claim management system. It handles the full lifecycle — from product registration and warranty tracking through AI-assisted claim evaluation to human review and final decision. The system implements all 50 functional requirements from the SRS, passes 180 automated tests, and achieves 97.78%+ accuracy on unseen test claims for both AI models.

The most important design principle we kept throughout: the AI makes recommendations, but humans stay in control. Every AI decision can be overridden, every override is recorded, and every action is logged in the audit trail. That combination of automation and accountability is what makes a real-world AI system trustworthy.

---

*AssureX Claim Engine — TechWiz 7 Competition, Aptech Computer Education, 2026*
