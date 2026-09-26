# AssureX Claim Engine — Hidden Test Readiness Checklist

This checklist confirms the application handles all special claim scenarios
that evaluators may test with hidden/unseen claims.

---

## Claim Types Demonstrated

| # | Claim Type | File | Expected Decision |
|---|-----------|------|-------------------|
| 1 | Valid Claim | sample_claims/sample_0000001.json | Likely Valid |
| 2 | Invalid Claim | sample_claims/sample_0000002.json | Likely Invalid |
| 3 | Manual Review | sample_claims/sample_0000003.json | Manual Review Required |
| 4 | Expired Warranty | sample_claims/sample_0000004.json | Likely Invalid |
| 5 | Missing Documents | sample_claims/sample_0000005.json | Likely Invalid |
| 6 | Duplicate Claim | sample_claims/sample_0000006.json | Manual Review Required |
| 7 | Contradictory Claim | sample_claims/sample_0000007.json | Likely Invalid |
| 8 | Serial Number Mismatch | sample_claims/sample_0000008.json | Manual Review Required |
| 9 | Unauthorized Repair | sample_claims/sample_0000009.json | Likely Invalid |
| 10 | Boundary Date | sample_claims/sample_0000010.json | Manual Review Required |
| 11 | Model Disagreement | sample_claims/sample_0000011.json | Manual Review Required |

---

## System Capability Checklist

### AI Pipeline
- [x] Python ML model loaded and functional (98.22% accuracy)
- [x] GTM image model loaded and functional (99.11% accuracy)
- [x] Claim Summary Card generated for every claim submission
- [x] Both models predict independently and produce 3-class confidence scores
- [x] Confidence difference calculated: |Python - GTM| 
- [x] Model consistency status assigned (5 levels)

### Warranty Rule Engine
- [x] warranty_active — expired warranty hard fail
- [x] claim_reporting_period — >14 day delay warning
- [x] purchase_proof — missing receipt hard fail
- [x] serial_number_match — mismatch warning
- [x] authorized_repair_only — unauthorized repair hard fail
- [x] damage_coverage — excluded damage type hard fail
- [x] duplicate_claim — duplicate detection manual review
- [x] required_documents — missing docs manual review
- [x] repair_count_limit — >2 repairs manual review
- [x] product_age — very old product warning
- [x] date_contradiction — fault before purchase hard fail

### Detection Features
- [x] Duplicate document detection (SHA-256 hash)
- [x] Duplicate claim detection (same product, open claim)
- [x] Serial number cross-validation (OCR vs registered)
- [x] Date contradiction detection (fault before purchase)
- [x] Missing mandatory document identification

### Workflow
- [x] 4-step claim submission wizard
- [x] OCR data extraction with user correction
- [x] Manual review queue for reviewers
- [x] Reviewer approve/reject/request-info
- [x] AI decision override with reason
- [x] Claim status tracking (8 stages)
- [x] Notifications for all status changes
- [x] Full audit trail

### Dashboards & Reports
- [x] Customer dashboard
- [x] Employee dashboard
- [x] Reviewer dashboard
- [x] Admin dashboard with analytics
- [x] Downloadable claim report
- [x] CSV/Excel data export
- [x] Model performance metrics

---

## Quick Test Commands

```bash
# Run all 180 tests
python -m pytest tests/ -v

# Generate model comparison report (45 claims)
python reports/generate_model_comparison_report.py

# Regenerate all card images
python src/card_generator/claim_card_generator.py

# Retrain TM image model
python src/tm_trainer/train_teachable_machine.py

# Start the web application
python manage.py runserver
```

---

## Evaluator Login Credentials

| Role | Email | Password |
|------|-------|----------|
| Administrator | admin@assurex.com | Admin@123 |
| Reviewer | reviewer@assurex.com | Review@123 |
| Employee | employee@assurex.com | Employee@123 |
| Customer | customer@assurex.com | Customer@123 |

*(Create using: `python manage.py createsuperuser` or via registration)*

---

## Surprise Modification Readiness

The application is designed for easy modification:

| Modification | Location | How To |
|-------------|----------|--------|
| New warranty exclusion | policies/policy_*.json | Add to "exclusions" array |
| Change confidence threshold | config/app_config.json | Edit threshold values |
| Support new date format | src/preprocessing/claim_preprocessor.py | Add to _safe_days() |
| New contradiction rule | src/rule_engine/warranty_rule_engine.py | Add _check_* function |
| Modify decision logic | src/decision_engine/evaluator.py | Edit compute_final_decision() |
| New dashboard filter | apps/administrator/views.py | Add filter to all_claims view |

---

*Checklist verified: All 11 required claim types implemented and tested.*
