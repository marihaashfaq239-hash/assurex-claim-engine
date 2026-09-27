# AssureX Claim Engine — Data Dictionary

**Project:** AssureX Claim Engine · NextWave AI and ML
**Team:** Muhammad Hunain (1538835) · Mariha Ashfaq (1540161) · Owais Ahmed (1515897) · Muhammad Daniyal (1542905)
**Institute / Competition:** Aptech Computer Education · TechWiz 7
**Version:** 1.0

---

## Contents

1. [DB Tables](#section-1--database-tables-16-tables) — All 16 database tables with full column-level detail
2. [ML Features](#section-2--ml-feature-dictionary-19-features) — 19 features used by the Python classification model
3. [Claim Status Flow](#section-3--claim-status-flow) — Full lifecycle of a claim
4. [Notification Types](#section-4--notification-types-12-types) — 12 in-app notification categories
5. [Audit Log Types](#section-5--audit-log-action-types-21-types) — 21 audit trail action types

---

## Section 1 — Database Tables (16 Tables)

### Table 01 · `users` · 17 columns

| Column | Data Type | Constraints | Description |
|--------|-----------|-------------|-------------|
| id | INTEGER | PK, Auto | Django internal ID |
| user_id | UUID | UNIQUE, NOT NULL | System-wide unique user identifier |
| email | VARCHAR(254) | UNIQUE, NOT NULL | Login email (USERNAME_FIELD) |
| first_name | VARCHAR(100) | NOT NULL | User's first name |
| last_name | VARCHAR(100) | NOT NULL | User's last name |
| role | VARCHAR(20) | NOT NULL | One of: customer, employee, reviewer, administrator |
| phone | VARCHAR(20) | NULLABLE | Contact phone number |
| address | TEXT | NULLABLE | Postal address |
| city | VARCHAR(100) | NULLABLE | City of residence |
| country | VARCHAR(100) | DEFAULT 'Pakistan' | Country |
| profile_pic | VARCHAR(255) | NULLABLE | Path to uploaded profile picture |
| is_active | BOOLEAN | DEFAULT True | Account active/inactive flag |
| is_staff | BOOLEAN | DEFAULT False | Django admin staff access |
| is_verified | BOOLEAN | DEFAULT False | Email verification flag |
| date_joined | DATETIME | AUTO | Account creation timestamp |
| last_login | DATETIME | NULLABLE | Last login timestamp |
| updated_at | DATETIME | AUTO_UPDATE | Last profile update |

---

### Table 02 · `product_categories` · 6 columns

| Column | Data Type | Constraints | Description |
|--------|-----------|-------------|-------------|
| id | INTEGER | PK, Auto | Internal ID |
| name | VARCHAR(100) | UNIQUE | Category name (e.g., Air Conditioner) |
| description | TEXT | NULLABLE | Category description |
| icon | VARCHAR(50) | NULLABLE | Bootstrap icon name |
| is_active | BOOLEAN | DEFAULT True | Active/inactive |
| created_at | DATETIME | AUTO | Creation timestamp |

---

### Table 03 · `products` · 18 columns

| Column | Data Type | Constraints | Description |
|--------|-----------|-------------|-------------|
| id | INTEGER | PK, Auto | Internal ID |
| product_id | UUID | UNIQUE | System-wide product identifier |
| owner_id | FK(users) | NOT NULL | Customer who owns the product |
| registered_by_id | FK(users) | NULLABLE | Employee who registered on behalf |
| product_name | VARCHAR(200) | NOT NULL | Product name (e.g., Split AC 1.5 Ton) |
| brand | VARCHAR(100) | NOT NULL | Manufacturer brand |
| category_id | FK(product_categories) | NOT NULL | Product category |
| model_number | VARCHAR(100) | NOT NULL | Model number from product label |
| serial_number | VARCHAR(200) | NOT NULL | Unique serial number |
| purchase_date | DATE | NOT NULL | Date of purchase |
| purchase_price | DECIMAL(12,2) | NULLABLE | Purchase price in PKR |
| retailer | VARCHAR(200) | NULLABLE | Retailer/shop name |
| purchase_city | VARCHAR(100) | NULLABLE | City of purchase |
| warranty_duration_months | INTEGER | NULLABLE | Warranty duration in months |
| notes | TEXT | NULLABLE | Additional notes |
| is_active | BOOLEAN | DEFAULT True | Soft-delete flag |
| created_at | DATETIME | AUTO | Registration timestamp |
| updated_at | DATETIME | AUTO_UPDATE | Last update |

---

### Table 04 · `warranties` · 16 columns

| Column | Data Type | Constraints | Description |
|--------|-----------|-------------|-------------|
| id | INTEGER | PK, Auto | Internal ID |
| warranty_id | UUID | UNIQUE | Warranty identifier |
| product_id | FK(products) | NOT NULL | Associated product |
| policy_id | FK(warranty_policies) | NULLABLE | Associated warranty policy |
| warranty_type | VARCHAR(20) | NOT NULL | standard / extended / third_party |
| warranty_provider | VARCHAR(200) | DEFAULT 'Manufacturer' | Provider name |
| service_center | VARCHAR(200) | NULLABLE | Authorized service center |
| start_date | DATE | NOT NULL | Warranty start date |
| expiry_date | DATE | NOT NULL | Warranty expiry date |
| coverage_description | TEXT | NULLABLE | What is covered |
| exclusions | TEXT | NULLABLE | What is excluded |
| status | VARCHAR(20) | NOT NULL | active / expired / expiring / extended / void |
| is_active | BOOLEAN | DEFAULT True | Active flag |
| warranty_card | VARCHAR(255) | NULLABLE | Uploaded warranty card file path |
| created_at | DATETIME | AUTO | Creation timestamp |
| updated_at | DATETIME | AUTO_UPDATE | Last update |

---

### Table 05 · `claims` · 38 columns

| Column | Data Type | Constraints | Description |
|--------|-----------|-------------|-------------|
| id | INTEGER | PK, Auto | Internal ID |
| claim_id | UUID | UNIQUE | Claim UUID |
| claim_reference | VARCHAR(20) | UNIQUE | Human-readable (e.g., CLM-0000001) |
| claimant_id | FK(users) | NOT NULL | Customer filing the claim |
| submitted_by_id | FK(users) | NULLABLE | Employee submitting on behalf |
| product_id | FK(products) | NOT NULL | Product being claimed |
| warranty_id | FK(warranties) | NULLABLE | Associated warranty |
| fault_date | DATE | NOT NULL | When fault was first noticed |
| fault_description | TEXT | NOT NULL | Description of the fault |
| damage_type | VARCHAR(30) | NOT NULL | physical/electrical/mechanical/etc. |
| fault_location | VARCHAR(200) | NULLABLE | Location of damage on product |
| additional_notes | TEXT | NULLABLE | Extra notes |
| status | VARCHAR(20) | DEFAULT 'draft' | draft/submitted/evaluation/additional/manual/approved/rejected/closed |
| final_decision | VARCHAR(20) | DEFAULT 'pending' | likely_valid/likely_invalid/manual_review/pending |
| decision_reason | TEXT | NULLABLE | Explanation of decision |
| python_prediction | VARCHAR(30) | NULLABLE | ML model class prediction |
| python_confidence_valid | FLOAT | NULLABLE | Confidence for valid_claim (0–1) |
| python_confidence_invalid | FLOAT | NULLABLE | Confidence for invalid_claim (0–1) |
| python_confidence_manual | FLOAT | NULLABLE | Confidence for manual_review (0–1) |
| tm_prediction | VARCHAR(30) | NULLABLE | TM model class prediction |
| tm_confidence_valid | FLOAT | NULLABLE | TM confidence for valid_claim |
| tm_confidence_invalid | FLOAT | NULLABLE | TM confidence for invalid_claim |
| tm_confidence_manual | FLOAT | NULLABLE | TM confidence for manual_review |
| confidence_difference | FLOAT | NULLABLE | Absolute diff between top-class confidences |
| model_consistency_status | VARCHAR(30) | NULLABLE | strong_match/acceptable_match/weak_match/model_disagreement/uncertain_result |
| rules_passed | INTEGER | DEFAULT 0 | Count of passed warranty rules |
| rules_failed | INTEGER | DEFAULT 0 | Count of failed warranty rules |
| rules_warning | INTEGER | DEFAULT 0 | Count of warning rules |
| is_duplicate | BOOLEAN | DEFAULT False | Duplicate flag |
| duplicate_of_id | FK(claims) | NULLABLE | Reference to original claim |
| python_model_version_id | FK(model_versions) | NULLABLE | Python model version used |
| tm_model_version_id | FK(model_versions) | NULLABLE | TM model version used |
| claim_card_image | VARCHAR(255) | NULLABLE | Generated claim summary card path |
| submission_date | DATETIME | NULLABLE | When claim was submitted |
| evaluated_at | DATETIME | NULLABLE | When AI evaluation completed |
| closed_at | DATETIME | NULLABLE | When claim was closed |
| created_at | DATETIME | AUTO | Creation timestamp |
| updated_at | DATETIME | AUTO_UPDATE | Last update |

---

### Table 06 · `claim_documents` · 12 columns

| Column | Data Type | Constraints | Description |
|--------|-----------|-------------|-------------|
| id | INTEGER | PK, Auto | Internal ID |
| doc_id | UUID | UNIQUE | Document identifier |
| claim_id | FK(claims) | NOT NULL | Associated claim |
| doc_type | VARCHAR(30) | NOT NULL | purchase_receipt/warranty_card/product_image/fault_evidence/repair_report/serial_photo/diagnostic/other |
| file | VARCHAR(255) | NOT NULL | File path |
| file_name | VARCHAR(255) | NOT NULL | Original filename |
| file_size | INTEGER | NOT NULL | Size in bytes |
| mime_type | VARCHAR(100) | NOT NULL | MIME type (application/pdf, image/jpeg, etc.) |
| file_hash | VARCHAR(64) | INDEXED | SHA-256 hash for duplicate detection |
| description | VARCHAR(300) | NULLABLE | Document description |
| uploaded_by_id | FK(users) | NULLABLE | Who uploaded |
| uploaded_at | DATETIME | AUTO | Upload timestamp |

---

### Table 07 · `ocr_results` · 23 columns

| Column | Data Type | Constraints | Description |
|--------|-----------|-------------|-------------|
| id | INTEGER | PK, Auto | Internal ID |
| ocr_id | UUID | UNIQUE | OCR result identifier |
| document_id | FK(claim_documents) | UNIQUE (1-to-1) | Document that was OCR'd |
| claim_id | FK(claims) | NOT NULL | Associated claim |
| invoice_number | VARCHAR(100) | NULLABLE | Extracted invoice/receipt number |
| product_name | VARCHAR(200) | NULLABLE | Product name from document |
| brand | VARCHAR(100) | NULLABLE | Brand name from document |
| model_number | VARCHAR(100) | NULLABLE | Model number from document |
| serial_number | VARCHAR(200) | NULLABLE | Serial number from document |
| purchase_date | DATE | NULLABLE | Purchase date extracted |
| purchase_amount | DECIMAL(12,2) | NULLABLE | Purchase amount extracted |
| retailer | VARCHAR(200) | NULLABLE | Retailer name extracted |
| warranty_duration | VARCHAR(50) | NULLABLE | Warranty duration text |
| raw_text | TEXT | NULLABLE | Full OCR raw text |
| extracted_data | JSON | DEFAULT {} | All extracted fields as JSON |
| status | VARCHAR(10) | NOT NULL | success / partial / failed |
| confidence | FLOAT | NULLABLE | OCR confidence score (0–1) |
| ocr_engine | VARCHAR(50) | DEFAULT 'tesseract' | OCR engine used |
| is_verified | BOOLEAN | DEFAULT False | User verified the data |
| verified_by_id | FK(users) | NULLABLE | Who verified |
| verification_notes | TEXT | NULLABLE | Verification notes |
| extracted_at | DATETIME | AUTO | When OCR was run |
| verified_at | DATETIME | NULLABLE | When verified |

---

### Table 08 · `repair_history` · 13 columns

| Column | Data Type | Constraints | Description |
|--------|-----------|-------------|-------------|
| id | INTEGER | PK, Auto | Internal ID |
| repair_id | UUID | UNIQUE | Repair identifier |
| claim_id | FK(claims) | NOT NULL | Associated claim |
| product_id | FK(products) | NOT NULL | Product repaired |
| repair_date | DATE | NOT NULL | Date of repair |
| repair_center | VARCHAR(200) | NOT NULL | Where repaired |
| is_authorized | BOOLEAN | DEFAULT True | Authorized service center? |
| replaced_parts | TEXT | NULLABLE | Parts replaced |
| repair_description | TEXT | NOT NULL | What was done |
| repair_cost | DECIMAL(10,2) | NULLABLE | Cost of repair |
| outcome | VARCHAR(20) | NOT NULL | fixed / partial / failed / replaced / pending |
| repair_report_file | VARCHAR(255) | NULLABLE | Repair report document |
| created_at | DATETIME | AUTO | Entry timestamp |

---

### Table 09 · `model_predictions` · 12 columns

| Column | Data Type | Constraints | Description |
|--------|-----------|-------------|-------------|
| id | INTEGER | PK, Auto | Internal ID |
| prediction_id | UUID | UNIQUE | Prediction identifier |
| claim_id | FK(claims) | NOT NULL | Claim evaluated |
| model_type | VARCHAR(30) | NOT NULL | python_ml / teachable_machine |
| model_version_id | FK(model_versions) | NULLABLE | Model version used |
| predicted_class | VARCHAR(20) | NOT NULL | valid_claim / invalid_claim / manual_review |
| confidence_valid | FLOAT | NOT NULL | Confidence for valid_claim (0–1) |
| confidence_invalid | FLOAT | NOT NULL | Confidence for invalid_claim (0–1) |
| confidence_manual_review | FLOAT | NOT NULL | Confidence for manual_review (0–1) |
| input_data | JSON | DEFAULT {} | Feature vector fed to model |
| processing_time_ms | INTEGER | NULLABLE | Prediction time in ms |
| created_at | DATETIME | AUTO | Prediction timestamp |

---

### Table 10 · `warranty_policies` · 22 columns

| Column | Data Type | Constraints | Description |
|--------|-----------|-------------|-------------|
| id | INTEGER | PK, Auto | Internal ID |
| policy_id | UUID | UNIQUE | Policy identifier |
| name | VARCHAR(200) | NOT NULL | Policy name |
| product_category_id | FK(product_categories) | NOT NULL | Applicable category |
| standard_duration_months | INTEGER | DEFAULT 12 | Standard warranty months |
| extended_duration_months | INTEGER | DEFAULT 0 | Extended warranty months |
| claim_reporting_period_days | INTEGER | DEFAULT 14 | Days to report after fault |
| covered_faults | JSON | DEFAULT [] | List of covered fault types |
| exclusions | JSON | DEFAULT [] | List of exclusions |
| mandatory_documents | JSON | DEFAULT [] | Required document types |
| authorized_repair_required | BOOLEAN | DEFAULT True | Auth repair required? |
| max_repair_count | INTEGER | DEFAULT 2 | Max previous repairs allowed |
| replacement_allowed | BOOLEAN | DEFAULT False | Product replacement allowed? |
| grace_period_days | INTEGER | DEFAULT 7 | Grace period after expiry |
| hard_fail_rules | JSON | DEFAULT [] | Rules that auto-invalidate |
| warning_rules | JSON | DEFAULT [] | Rules that add warnings |
| manual_review_rules | JSON | DEFAULT [] | Rules routing to manual review |
| policy_file | VARCHAR(255) | NULLABLE | Source JSON filename |
| is_active | BOOLEAN | DEFAULT True | Active flag |
| created_by_id | FK(users) | NULLABLE | Who created/loaded |
| created_at | DATETIME | AUTO | Creation timestamp |
| updated_at | DATETIME | AUTO_UPDATE | Last update |

---

### Table 11 · `rule_results` · 8 columns

| Column | Data Type | Constraints | Description |
|--------|-----------|-------------|-------------|
| id | INTEGER | PK, Auto | Internal ID |
| claim_id | FK(claims) | NOT NULL | Claim evaluated |
| rule_name | VARCHAR(200) | NOT NULL | Name of the rule checked |
| rule_type | VARCHAR(20) | NOT NULL | hard_fail / warning / manual_review |
| outcome | VARCHAR(10) | NOT NULL | pass / fail / warning / skip |
| description | TEXT | NULLABLE | Human-readable result |
| detail | JSON | DEFAULT {} | Detailed result data |
| created_at | DATETIME | AUTO | When rule was checked |

---

### Table 12 · `reviews` · 15 columns

| Column | Data Type | Constraints | Description |
|--------|-----------|-------------|-------------|
| id | INTEGER | PK, Auto | Internal ID |
| review_id | UUID | UNIQUE | Review identifier |
| claim_id | FK(claims) | UNIQUE (1-to-1) | Claim being reviewed |
| reviewer_id | FK(users) | NULLABLE | Assigned reviewer |
| python_prediction | VARCHAR(30) | NULLABLE | Python model result shown to reviewer |
| tm_prediction | VARCHAR(30) | NULLABLE | TM result shown to reviewer |
| model_consistency | VARCHAR(30) | NULLABLE | Consistency status shown |
| decision | VARCHAR(20) | DEFAULT 'pending' | approved / rejected / more_info / pending |
| reviewer_comments | TEXT | NOT NULL | Reviewer's comments |
| additional_info_request | TEXT | NULLABLE | What additional info was requested |
| is_ai_override | BOOLEAN | DEFAULT False | Did reviewer override AI? |
| ai_original_result | VARCHAR(30) | NULLABLE | What AI originally decided |
| override_reason | TEXT | NULLABLE | Reason for override |
| assigned_at | DATETIME | AUTO | When assigned to reviewer |
| reviewed_at | DATETIME | NULLABLE | When decision was made |

---

### Table 13 · `notifications` · 14 columns

| Column | Data Type | Constraints | Description |
|--------|-----------|-------------|-------------|
| id | INTEGER | PK, Auto | Internal ID |
| notification_id | UUID | UNIQUE | Notification identifier |
| recipient_id | FK(users) | NOT NULL | Who receives it |
| notification_type | VARCHAR(30) | NOT NULL | See Notification Types section |
| priority | VARCHAR(10) | DEFAULT 'medium' | low / medium / high / critical |
| title | VARCHAR(200) | NOT NULL | Notification title |
| message | TEXT | NOT NULL | Full notification message |
| link | VARCHAR(500) | NULLABLE | URL to navigate to |
| object_type | VARCHAR(50) | NULLABLE | Related object type (Claim, Warranty) |
| object_id | VARCHAR(100) | NULLABLE | Related object ID |
| is_read | BOOLEAN | DEFAULT False | Read status |
| read_at | DATETIME | NULLABLE | When read |
| is_emailed | BOOLEAN | DEFAULT False | Email sent? |
| created_at | DATETIME | AUTO | Creation timestamp |

---

### Table 14 · `audit_logs` · 11 columns

| Column | Data Type | Constraints | Description |
|--------|-----------|-------------|-------------|
| id | INTEGER | PK, Auto | Internal ID |
| log_id | UUID | UNIQUE | Log entry identifier |
| user_id | FK(users) | NULLABLE | Who performed the action |
| action_type | VARCHAR(50) | NOT NULL | See Audit Log Action Types section |
| description | TEXT | NOT NULL | Human-readable description |
| ip_address | INET | NULLABLE | Client IP address |
| user_agent | VARCHAR(300) | NULLABLE | Browser user agent |
| object_type | VARCHAR(50) | NULLABLE | Related object type |
| object_id | VARCHAR(100) | NULLABLE | Related object ID |
| extra_data | JSON | DEFAULT {} | Additional structured data |
| created_at | DATETIME | AUTO | Log timestamp |

---

### Table 15 · `model_versions` · 11 columns

| Column | Data Type | Constraints | Description |
|--------|-----------|-------------|-------------|
| id | INTEGER | PK, Auto | Internal ID |
| version_id | UUID | UNIQUE | Version identifier |
| model_type | VARCHAR(30) | NOT NULL | python_ml / teachable_machine |
| version_name | VARCHAR(100) | NOT NULL | Version label (e.g., v1.0) |
| description | TEXT | NULLABLE | Version notes |
| file_path | VARCHAR(500) | NULLABLE | Path to saved model file |
| accuracy | FLOAT | NULLABLE | Test accuracy (0–1) |
| is_active | BOOLEAN | DEFAULT True | Currently active version |
| trained_at | DATETIME | NULLABLE | Training timestamp |
| created_at | DATETIME | AUTO | Registration timestamp |
| created_by_id | FK(users) | NULLABLE | Who registered this version |

---

### Table 16 · `system_configuration` · 8 columns

| Column | Data Type | Constraints | Description |
|--------|-----------|-------------|-------------|
| id | INTEGER | PK, Auto | Internal ID |
| config_id | UUID | UNIQUE | Config identifier |
| key | VARCHAR(100) | UNIQUE | Config key (e.g., confidence_threshold_min) |
| value | TEXT | NOT NULL | Config value |
| value_type | VARCHAR(10) | NOT NULL | str / int / float / bool / json |
| description | TEXT | NULLABLE | What this setting controls |
| updated_by_id | FK(users) | NULLABLE | Last updated by |
| updated_at | DATETIME | AUTO_UPDATE | Last update |

---

## Section 2 — ML Feature Dictionary (19 Features)

| # | Feature Name | Type | Range / Values | Description |
|---|-------------|------|----------------|-------------|
| 1 | product_category | String (Categorical) | Air Conditioner, Refrigerator, Washing Machine, Television, Smartphone, Laptop, Microwave, Generator, Water Heater, Small Appliance | Product type |
| 2 | brand | String (Categorical) | Samsung, LG, Haier, PEL, Dawlance, Orient, TCL, Sony, etc. | Manufacturer brand |
| 3 | damage_type | String (Categorical) | physical, electrical, mechanical, software, manufacturing, water, overheating, battery, display, other | Primary fault type |
| 4 | warranty_type | String (Categorical) | standard, extended, third_party | Warranty coverage type |
| 5 | product_age_months | Integer | 0–240 | Months since purchase date |
| 6 | warranty_remaining_days | Integer | -999 to 1800 | Days left on warranty (-ve = expired) |
| 7 | days_since_fault | Integer | 0–365 | Days between fault date and submission |
| 8 | has_receipt | Binary (0/1) | 0 or 1 | Purchase receipt uploaded |
| 9 | has_warranty_card | Binary (0/1) | 0 or 1 | Warranty card uploaded |
| 10 | has_product_image | Binary (0/1) | 0 or 1 | Product image uploaded |
| 11 | has_fault_evidence | Binary (0/1) | 0 or 1 | Fault evidence uploaded |
| 12 | repair_count | Integer | 0–10 | Number of previous repairs |
| 13 | has_unauthorized_repair | Binary (0/1) | 0 or 1 | Any unauthorized repairs |
| 14 | is_warranty_active | Binary (0/1) | 0 or 1 | Warranty currently active |
| 15 | serial_number_match | Binary (0/1) | 0 or 1 | Serial matches OCR-extracted |
| 16 | missing_documents_count | Integer | 0–4 | Number of missing mandatory docs |
| 17 | is_duplicate_flag | Binary (0/1) | 0 or 1 | Duplicate detection flag |
| 18 | purchase_price_pkr | Float | 0–2,000,000 | Purchase price in PKR |
| 19 | claim_reporting_within_period | Binary (0/1) | 0 or 1 | Reported within policy deadline |

> **Encoding:** String categoricals → `OneHotEncoder` via sklearn `ColumnTransformer`. Numerical features → `StandardScaler`. Binary features pass through unchanged.

### Claim Classes

| Class | Label | Description | Dataset Count |
|-------|-------|-------------|---------------|
| Valid Claim | `valid_claim` | Claim meets all criteria — warranty active, documents present, no contradictions | 500 records |
| Invalid Claim | `invalid_claim` | Claim fails validation — expired warranty, physical damage, unauthorized repair, duplicate | 500 records |
| Manual Review | `manual_review` | Borderline case — low confidence, conflicting info, missing key documents | 500 records |

> **Total:** 1,500 records · **Split:** 70% train (1,050) · 15% validation (225) · 15% test (225)

---

## Section 3 — Claim Status Flow

| Step | Status | Description |
|------|--------|-------------|
| 1 | **Draft** | Claim created but not yet submitted by the claimant. |
| 2 | **Submitted** | Claim has been submitted and is queued for AI evaluation. |
| 3 | **Under Evaluation** | OCR, ML models, and rule engine are actively processing the claim. |
| 4 | **Additional Info Required** | System or reviewer has requested more documents/details from the claimant. |
| 5 | **Manual Review** | Claim routed to a human reviewer due to model disagreement, low confidence, or rule warning. |
| 6a | **Approved** | Reviewer or AI confirmed the claim as valid (final). |
| 6b | **Rejected** | Reviewer or AI confirmed the claim as invalid (final). |
| 7 | **Closed** | Claim lifecycle complete; no further action possible. |

```
Draft → Submitted → Under Evaluation → Additional Info Required
                                     ↓
                              Manual Review → Approved / Rejected → Closed
```

---

## Section 4 — Notification Types (12 Types)

| # | Notification Type | Description |
|---|-------------------|-------------|
| 1 | `claim_submitted` | Sent to claimant when their claim is successfully submitted. |
| 2 | `claim_evaluated` | Sent when the AI pipeline finishes evaluating a claim. |
| 3 | `warranty_expiry` | Sent when a product's warranty is nearing or has reached expiry. |
| 4 | `reviewer_assigned` | Sent to a reviewer when a claim is assigned to their queue. |
| 5 | `claim_approved` | Sent to claimant when their claim is approved. |
| 6 | `claim_rejected` | Sent to claimant when their claim is rejected. |
| 7 | `more_info_requested` | Sent when a reviewer requests additional information. |
| 8 | `status_changed` | Sent whenever a claim's status transitions. |
| 9 | `duplicate_detected` | Sent when the system flags a claim as a possible duplicate. |
| 10 | `model_disagreement` | Sent internally when the two AI models disagree on a claim. |
| 11 | `system` | General system-level notification (maintenance, updates, etc.). |
| 12 | `general` | Miscellaneous/uncategorized notification. |

---

## Section 5 — Audit Log Action Types (21 Types)

| # | Action Type | Description |
|---|-------------|-------------|
| 1 | `account_created` | A new user account was registered. |
| 2 | `login` | A user logged into the system. |
| 3 | `logout` | A user logged out of the system. |
| 4 | `product_registered` | A new product was registered under a customer. |
| 5 | `warranty_added` | A warranty record was created for a product. |
| 6 | `document_uploaded` | A claim document was uploaded. |
| 7 | `ocr_extracted` | OCR extraction was run on an uploaded document. |
| 8 | `data_corrected` | A claimant corrected OCR-extracted data. |
| 9 | `claim_created` | A new claim record (draft) was created. |
| 10 | `claim_submitted` | A claim was submitted for evaluation. |
| 11 | `claim_status_changed` | A claim's status field was updated. |
| 12 | `model_predicted` | An AI model produced a prediction for a claim. |
| 13 | `reviewer_action` | A reviewer took an action on a claim. |
| 14 | `final_decision` | The system recorded a claim's final decision. |
| 15 | `ai_override` | A reviewer overrode the AI's recommendation. |
| 16 | `report_exported` | A report or data export was generated. |
| 17 | `user_managed` | An administrator created, edited, or deactivated a user. |
| 18 | `policy_updated` | A warranty policy JSON file was updated. |
| 19 | `threshold_updated` | An AI confidence threshold was changed by an admin. |
| 20 | `anomaly_detected` | The system flagged unusual claim activity. |
| 21 | `profile_updated` | A user updated their own profile information. |

---

*AssureX Claim Engine · TechWiz 7 · Aptech Computer Education · 2026*
