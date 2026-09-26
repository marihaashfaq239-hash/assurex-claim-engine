# AssureX — Application Screenshots

This folder contains screenshots of the running AssureX Claim Engine application.

## How to Generate Screenshots

1. Start the development server:
   ```
   python manage.py runserver
   ```

2. Open `http://127.0.0.1:8000` in your browser.

3. Capture screenshots of the following pages (listed below).

---

## Required Screenshots Checklist

### Authentication
- [ ] `01_login.png` — Login page
- [ ] `02_register_customer.png` — Register page with Customer role selected
- [ ] `03_register_employee.png` — Register page with Service Center Employee role selected

### Customer Dashboard & Products
- [ ] `04_customer_dashboard.png` — Customer dashboard overview
- [ ] `05_product_register.png` — Product registration form
- [ ] `06_product_list.png` — Registered products list
- [ ] `07_warranty_list.png` — Warranty list with status (active/expiring/expired)
- [ ] `08_warranty_expiry_alert.png` — Warranty expiry notification alert

### Claim Submission (4-Step Wizard)
- [ ] `09_claim_step1.png` — Step 1: Fault details form
- [ ] `10_claim_step2.png` — Step 2: Document upload + OCR extraction
- [ ] `11_claim_step3.png` — Step 3: Repair history
- [ ] `12_claim_step4.png` — Step 4: Review & Submit (with contradiction warnings if any)

### AI Evaluation & Results
- [ ] `13_claim_detail_ai_summary.png` — Claim detail — AI-Generated Claim Summary section
- [ ] `14_claim_detail_models.png` — Claim detail — Python ML + Teachable Machine confidence bars
- [ ] `15_claim_detail_rule_engine.png` — Claim detail — Warranty Rule Check results
- [ ] `16_claim_detail_decision.png` — Claim detail — Final Decision banner
- [ ] `17_contradiction_panel.png` — Claim detail — Contradiction & Inconsistency Report panel
- [ ] `18_claim_card_image.png` — Claim Summary Card image displayed on claim detail

### Claim Report
- [ ] `19_claim_report.png` — Downloadable claim report (HTML/print view)

### Manual Review
- [ ] `20_reviewer_queue.png` — Reviewer's manual review queue
- [ ] `21_reviewer_decision.png` — Reviewer making a decision + comments

### Administrator
- [ ] `22_admin_dashboard.png` — Admin dashboard with stats
- [ ] `23_admin_users.png` — User management with role assignment
- [ ] `24_admin_all_claims.png` — All claims view with filters
- [ ] `25_admin_analytics.png` — Analytics & charts
- [ ] `26_admin_export.png` — CSV export page
- [ ] `27_admin_thresholds.png` — AI threshold configuration
- [ ] `28_admin_audit_logs.png` — Audit logs

### Notifications
- [ ] `29_notifications.png` — Notification list (warranty expiry, claim updates)

### Edge Cases (SRS §1.10 — Test Demonstrations)
- [ ] `30_valid_claim.png` — A "Likely Valid" claim result
- [ ] `31_invalid_claim.png` — A "Likely Invalid" claim result
- [ ] `32_manual_review_claim.png` — A "Manual Review Required" result
- [ ] `33_model_disagreement.png` — Case where Python ML and TM models disagree
- [ ] `34_duplicate_claim.png` — Duplicate claim flagged
- [ ] `35_serial_mismatch.png` — Serial number mismatch contradiction

---

## Naming Convention

Use descriptive filenames: `{number}_{feature}.png`
Example: `01_login.png`, `13_claim_detail_ai_summary.png`

All screenshots should be in **PNG format**, minimum resolution **1280×720**.
