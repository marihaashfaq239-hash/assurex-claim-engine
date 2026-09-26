# AssureX Claim Engine — Test Cases Document

**Project:** AssureX Claim Engine — NextWave AI and ML  
**Team:** Muhammad Hunain (1538835), Mariha Ashfaq (1540161), Owais Ahmed (1515897), Muhammad Daniyal (1542905)  
**Version:** 1.0  

---

## Test Case Summary

| Category | Count |
|----------|-------|
| Functional Tests | 18 |
| Integration Tests | 6 |
| Boundary Tests | 5 |
| Negative Tests | 7 |
| Security Tests | 5 |
| ML Model Tests | 6 |
| OCR Tests | 4 |
| Rule Engine Tests | 6 |
| Mandatory SRS Scenarios | 11 |
| **Total** | **68** |

---

## Part 1 — Mandatory SRS Scenarios (11 Required)

### SRS-01: Valid Claim
**Precondition:** Customer registered, product registered (within warranty), all documents uploaded  
**Steps:**
1. Login as customer
2. Register Samsung AC (purchase 3 months ago, 24 months warranty)
3. Submit claim: Mechanical Failure, upload receipt + warranty card + product image + fault evidence
4. No unauthorized repairs, no missing documents
5. Submit and wait for AI evaluation

**Expected Result:** Final decision = **Likely Valid**, Python confidence_valid > 85%, TM confidence_valid > 85%, Strong Match consistency  
**Actual Result:** ✅ Likely Valid — Python 94.2%, TM 91.8%

---

### SRS-02: Invalid Claim — Expired Warranty
**Precondition:** Product registered 3 years ago, 12-month warranty (expired 2 years ago)  
**Steps:**
1. Register old product (purchase date: 3 years ago)
2. Submit claim with all documents
3. Complete all 4 steps

**Expected Result:** Final decision = **Likely Invalid**, rule_result shows warranty_expired = FAIL  
**Actual Result:** ✅ Likely Invalid — Warranty expired rule hard-fail triggered

---

### SRS-03: Manual Review Required
**Precondition:** Product with conflicting OCR data (serial mismatch)  
**Steps:**
1. Upload receipt with different serial number than registered
2. Complete claim submission
3. Both models return borderline confidence (<70%)

**Expected Result:** Claim routed to **Manual Review Required**, appears in reviewer queue  
**Actual Result:** ✅ Manual Review — Serial mismatch + low confidence triggers manual routing

---

### SRS-04: Expired Warranty Claim
**Precondition:** Warranty expired exactly 5 days ago (within grace period)  
**Steps:**
1. Product with expiry date = today - 5 days
2. Submit claim with all documents

**Expected Result:** Warning shown (within grace period), routed for manual review  
**Actual Result:** ✅ Warning generated, manual review triggered per policy grace period rules

---

### SRS-05: Missing Document Claim
**Precondition:** Customer uploads only product image, skips receipt and warranty card  
**Steps:**
1. Start claim submission
2. Step 2: Upload only product_image, skip other documents
3. Proceed to Step 4

**Expected Result:** Step 4 shows missing documents warning: "purchase_receipt, warranty_card required"  
**Actual Result:** ✅ Missing documents listed, hard_fail if mandatory docs absent per policy

---

### SRS-06: Duplicate Claim
**Precondition:** Claim already submitted for same product with same receipt  
**Steps:**
1. Submit claim-1 for Product A with receipt-X
2. Submit claim-2 for Product A with same receipt-X file
3. Check document hash detection

**Expected Result:** Warning "document has been used in another claim", is_duplicate flag set  
**Actual Result:** ✅ SHA-256 hash match detected, duplicate warning displayed

---

### SRS-07: Contradictory Claim
**Precondition:** Fault date set before product purchase date  
**Steps:**
1. Register product (purchase: 2024-06-01)
2. Submit claim with fault_date = 2024-05-15 (before purchase)
3. Proceed to Step 4

**Expected Result:** Contradiction detected — "fault date before purchase date", hard error shown  
**Actual Result:** ✅ Contradiction #1 triggers hard block on Step 4 submission

---

### SRS-08: Serial Number Mismatch
**Precondition:** OCR extracts different serial from receipt than registered serial  
**Steps:**
1. Register product serial: AC-12345
2. Upload receipt with OCR-extracted serial: AC-99999
3. Complete submission

**Expected Result:** Contradiction warning "serial number mismatch between registered and OCR-extracted"  
**Actual Result:** ✅ serial_number_match = 0, warning generated, claim routed for manual review

---

### SRS-09: Unauthorized Repair Claim
**Precondition:** Claim with repair history showing unauthorized repair center  
**Steps:**
1. Step 3: Add repair history entry, uncheck "Authorized Service Center"
2. Submit claim

**Expected Result:** Rule engine fails `check_unauthorized_repair`, warning or manual review triggered  
**Actual Result:** ✅ Rule warning generated, affects final decision confidence

---

### SRS-10: Boundary Date Claim
**Precondition:** Fault date exactly on warranty expiry date  
**Steps:**
1. Product warranty expires: 2026-09-20
2. Fault date: 2026-09-20 (same day)
3. Submit claim

**Expected Result:** Claim accepted (within warranty), status shows "expiring" boundary case, may route to manual review  
**Actual Result:** ✅ Boundary handled — within warranty, routes to manual review per borderline policy

---

### SRS-11: Model Disagreement Case
**Precondition:** Designed claim scenario where models give different predictions  
**Steps:**
1. Create claim with mixed signals: warranty active, documents present, but unauthorized repair + serial mismatch
2. Submit claim
3. Check model comparison

**Expected Result:** Python and TM predict different classes, model_consistency_status = model_disagreement, final = Manual Review Required  
**Actual Result:** ✅ Model disagreement detected, auto-routed to manual review

---

## Part 2 — Functional Tests

### FT-01: User Registration
**Test:** Customer self-registration with valid data  
**Input:** first_name=Ali, last_name=Hassan, email=ali@test.com, password=Test@1234, role=customer  
**Expected:** Account created, auto-login, redirect to customer dashboard  
**Result:** ✅ Pass

### FT-02: User Registration — Duplicate Email
**Test:** Registration with already-registered email  
**Input:** email=ali@test.com (already exists)  
**Expected:** Form error "An account with this email already exists"  
**Result:** ✅ Pass

### FT-03: Login with Valid Credentials
**Input:** email=admin@assurex.com, password=Admin@123  
**Expected:** Login success, redirect to admin dashboard  
**Result:** ✅ Pass

### FT-04: Login with Wrong Password
**Input:** email=admin@assurex.com, password=wrongpass  
**Expected:** Error "Incorrect email or password"  
**Result:** ✅ Pass

### FT-05: Role-Based Dashboard Redirect
**Test:** Each role redirects to correct dashboard after login  
**Expected:** customer→/dashboard/customer/, employee→/dashboard/employee/, reviewer→/dashboard/reviewer/, admin→/dashboard/admin/  
**Result:** ✅ Pass (all 4 roles)

### FT-06: Product Registration
**Input:** All required fields, valid serial number  
**Expected:** Product created, warranty auto-generated, product appears in list  
**Result:** ✅ Pass

### FT-07: Claim Step 1 — Draft Creation
**Test:** Fill fault details, click Next  
**Expected:** Draft claim created (status=draft), redirect to Step 2  
**Result:** ✅ Pass

### FT-08: Claim Step 2 — Document Upload
**Test:** Upload valid PDF receipt  
**Expected:** Document saved, OCR runs, extracted fields shown  
**Result:** ✅ Pass

### FT-09: OCR Data Verification
**Test:** Edit OCR-extracted serial number field  
**Expected:** Updated value saved, is_verified=True  
**Result:** ✅ Pass

### FT-10: Claim Step 3 — Repair History
**Test:** Add repair entry, then delete it  
**Expected:** Entry added and removed correctly  
**Result:** ✅ Pass

### FT-11: Claim Submission (Step 4)
**Test:** Submit valid claim  
**Expected:** Status changes draft→submitted→evaluation, AI pipeline triggered, notification sent  
**Result:** ✅ Pass

### FT-12: Reviewer — Approve Claim
**Test:** Reviewer approves manual_review claim  
**Expected:** Claim status = approved, customer notified  
**Result:** ✅ Pass

### FT-13: Reviewer — AI Override
**Test:** Reviewer changes decision, is_ai_override=True  
**Expected:** Override saved, ai_original_result stored, audit log entry created  
**Result:** ✅ Pass

### FT-14: Admin — Change User Role
**Test:** Admin changes user role from customer to reviewer  
**Expected:** Role updated, audit log entry created  
**Result:** ✅ Pass

### FT-15: Admin — Update AI Threshold
**Test:** Change confidence_threshold_min from 0.70 to 0.65  
**Expected:** Value saved, success message shown  
**Result:** ✅ Pass

### FT-16: CSV Export
**Test:** Admin exports claims CSV  
**Expected:** CSV file downloaded with all claim columns  
**Result:** ✅ Pass

### FT-17: Password Reset Flow
**Test:** Request password reset for registered email  
**Expected:** Reset link sent (console), new password accepted  
**Result:** ✅ Pass

### FT-18: Manual Warranty Add
**Test:** Customer adds extended warranty manually  
**Expected:** Warranty created, notification sent  
**Result:** ✅ Pass

---

## Part 3 — Integration Tests

### IT-01: Full Claim Pipeline (End-to-End)
**Test:** Complete flow from registration to AI decision  
**Steps:** Register user → Register product → Submit 4-step claim → Check AI result  
**Expected:** All steps complete, AI result populated in claim  
**Result:** ✅ Pass

### IT-02: OCR → Contradiction Detection
**Test:** OCR extracts different date → Step 4 shows contradiction  
**Expected:** Contradiction "purchase date mismatch between OCR and entered data"  
**Result:** ✅ Pass

### IT-03: Reviewer Queue Population
**Test:** Submit claim that routes to manual_review → Appears in reviewer queue  
**Expected:** Claim visible in /reviewer/queue/ immediately after AI evaluation  
**Result:** ✅ Pass

### IT-04: Notification → Unread Count
**Test:** Submit claim → Check navbar notification count  
**Expected:** Unread count increases by 1  
**Result:** ✅ Pass

### IT-05: AI Threshold → Decision Change
**Test:** Lower confidence threshold → Previously borderline claim now auto-decided  
**Expected:** Claims with 65-70% confidence auto-decide after threshold change  
**Result:** ✅ Pass

### IT-06: Audit Trail Completeness
**Test:** Perform login, product register, claim submit, reviewer approve  
**Expected:** All 4 actions appear in audit log with correct action_type  
**Result:** ✅ Pass

---

## Part 4 — Boundary Tests

### BT-01: Exactly 5MB File Upload
**Test:** Upload 5.0MB PDF  
**Expected:** Upload succeeds (at limit)  
**Result:** ✅ Pass

### BT-02: 5.01MB File Upload
**Test:** Upload file slightly over 5MB  
**Expected:** Error "File too large. Maximum size is 5MB"  
**Result:** ✅ Pass

### BT-03: Fault Date = Today
**Test:** Set fault_date to today's date  
**Expected:** days_since_fault = 0, valid submission  
**Result:** ✅ Pass

### BT-04: Warranty Expiring Today
**Test:** Warranty expiry = today  
**Expected:** Status = expiring, alert sent, claim accepted  
**Result:** ✅ Pass

### BT-05: Zero Previous Repairs
**Test:** Submit claim with repair_count = 0  
**Expected:** repair_count feature = 0, no unauthorized repair flag  
**Result:** ✅ Pass

---

## Part 5 — Negative Tests

### NT-01: Upload Non-PDF/Image File
**Test:** Upload .exe file  
**Expected:** Error "File type not allowed. Use PDF, JPG, or PNG"  
**Result:** ✅ Pass

### NT-02: Empty Fault Description
**Test:** Submit Step 1 with blank fault_description  
**Expected:** Form validation error "This field is required"  
**Result:** ✅ Pass

### NT-03: Future Fault Date
**Test:** Set fault_date = tomorrow  
**Expected:** Step 4 contradiction error "fault date is in the future"  
**Result:** ✅ Pass

### NT-04: Access Reviewer Dashboard as Customer
**Test:** Visit /reviewer/queue/ as customer  
**Expected:** 403 Forbidden — "Access denied. Reviewer role required"  
**Result:** ✅ Pass

### NT-05: Access Admin Dashboard as Employee
**Test:** Visit /administrator/users/ as employee  
**Expected:** 403 Forbidden  
**Result:** ✅ Pass

### NT-06: Submit Claim for Another User's Product
**Test:** Manually craft POST to submit claim with another user's product_id  
**Expected:** 404 — product not found (queryset scoped to request.user)  
**Result:** ✅ Pass

### NT-07: Invalid Password Reset Token
**Test:** Access /accounts/password-reset/abc/invalid-token/  
**Expected:** "This link is invalid or has expired" message  
**Result:** ✅ Pass

---

## Part 6 — Security Tests

### ST-01: CSRF Protection
**Test:** POST without CSRF token  
**Expected:** 403 Forbidden  
**Result:** ✅ Pass

### ST-02: SQL Injection in Search
**Test:** Search field input: `' OR '1'='1`  
**Expected:** No DB error, treated as literal string, 0 results  
**Result:** ✅ Pass (Django ORM parameterized queries)

### ST-03: XSS in Claim Description
**Test:** fault_description: `<script>alert('xss')</script>`  
**Expected:** Stored as literal text, rendered as escaped HTML, no script execution  
**Result:** ✅ Pass (Django auto-escaping)

### ST-04: Unauthenticated Access
**Test:** Visit /claims/my/ without login  
**Expected:** Redirect to /accounts/login/?next=/claims/my/  
**Result:** ✅ Pass

### ST-05: Brute Force — Password
**Test:** 10 rapid wrong password attempts  
**Expected:** No lockout (not implemented), but wrong password error each time, no information leakage  
**Result:** ✅ Pass (no account enumeration)

---

## Part 7 — ML Model Tests

### ML-01: Python Model Accuracy
**Test:** Run model on 225-record test CSV  
**Expected:** Overall accuracy ≥ 85% (SRS target)  
**Actual:** 97.78% ✅ Pass

### ML-02: TM Model Accuracy
**Test:** Run TM model on 225-record test set  
**Expected:** Overall accuracy ≥ 85%  
**Actual:** 97.78% ✅ Pass

### ML-03: Feature Count Verification
**Test:** Check model input feature count  
**Expected:** 19 features match ALL_FEATURES list  
**Result:** ✅ Pass

### ML-04: Confidence Score Sum
**Test:** Sum of 3 confidence scores for one prediction  
**Expected:** Sum ≈ 1.0 (±0.001)  
**Result:** ✅ Pass

### ML-05: Model Consistency — Strong Match
**Test:** Both models same class, diff = 3%  
**Expected:** model_consistency_status = strong_match  
**Result:** ✅ Pass

### ML-06: Model Consistency — Disagreement
**Test:** Python = valid_claim, TM = invalid_claim  
**Expected:** model_consistency_status = model_disagreement, final = Manual Review  
**Result:** ✅ Pass

---

## Part 8 — OCR Tests

### OCR-01: Receipt Upload — Date Extraction
**Test:** Upload clear receipt image  
**Expected:** purchase_date extracted correctly  
**Result:** ✅ Pass

### OCR-02: Receipt Upload — Amount Extraction
**Test:** Upload receipt with PKR 150,000  
**Expected:** purchase_amount = 150000.00  
**Result:** ✅ Pass

### OCR-03: Poor Quality Image
**Test:** Upload blurry/low-resolution image  
**Expected:** OCR status = partial, raw_text populated, some fields blank  
**Result:** ✅ Pass

### OCR-04: Non-Receipt Document
**Test:** Upload product image as purchase_receipt type  
**Expected:** OCR runs, fields mostly blank, status = partial  
**Result:** ✅ Pass

---

## Part 9 — Rule Engine Tests

### RE-01: Warranty Expired Hard Fail
**Test:** Product warranty expired 6 months ago  
**Expected:** check_warranty_expiry = FAIL (hard_fail), final = Likely Invalid  
**Result:** ✅ Pass

### RE-02: Claim Reporting Period
**Test:** Fault date was 20 days ago, policy requires 14-day reporting  
**Expected:** check_claim_reporting_period = WARNING  
**Result:** ✅ Pass

### RE-03: Max Repair Count Exceeded
**Test:** 3 previous repairs, policy max = 2  
**Expected:** check_repair_count = FAIL  
**Result:** ✅ Pass

### RE-04: Excluded Damage Type
**Test:** Damage type = water (excluded in policy)  
**Expected:** check_covered_faults = FAIL  
**Result:** ✅ Pass

### RE-05: Missing Mandatory Documents
**Test:** Policy requires purchase_receipt, but not uploaded  
**Expected:** check_mandatory_documents = FAIL  
**Result:** ✅ Pass

### RE-06: All Rules Pass
**Test:** Ideal claim — all conditions met  
**Expected:** All 9 rules = PASS, rules_failed = 0  
**Result:** ✅ Pass
