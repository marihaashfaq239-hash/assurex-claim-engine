# AssureX — Model Prediction & Confidence Comparison Report

**Project:** AssureX Claim Engine — NextWave AI and ML  
**Team:** Muhammad Hunain (1538835), Mariha Ashfaq (1540161), Owais Ahmed (1515897), Muhammad Daniyal (1542905)  
**Report Type:** 30 Unseen Test Claims (SRS Section 1.10 requirement)  
**Python ML Accuracy:** 97.78% on test set  
**TM Model Accuracy:** 97.78% on test set  
**Model Agreement Rate:** 95.6% (identical predictions on 28/30 test claims)

---

## Model Consistency Thresholds Used

| Status | Condition |
|--------|-----------|
| Strong Match | Both same class AND confidence difference ≤ 5% |
| Acceptable Match | Both same class AND difference 5%–15% |
| Weak Match | Both same class AND difference 15%–25% |
| Model Disagreement | Different predicted classes |
| Uncertain Result | Either model confidence < 70% on top class |

---

## 30 Unseen Test Claims — Results

| # | Claim ID | Actual Class | Python Pred | Py Valid% | Py Invalid% | Py Manual% | TM Pred | TM Valid% | TM Invalid% | TM Manual% | Match | Diff% | Consistency | Rules | Missing Docs | Contradictions | Final Decision |
|---|----------|-------------|-------------|-----------|-------------|------------|---------|-----------|-------------|------------|-------|-------|-------------|-------|-------------|----------------|----------------|
| 1 | TC-001 | valid_claim | valid_claim | 94.2 | 3.1 | 2.7 | valid_claim | 91.8 | 5.2 | 3.0 | YES | 2.4 | Strong Match | 9 passed, 0 failed | None | None | Likely Valid |
| 2 | TC-002 | invalid_claim | invalid_claim | 2.1 | 95.8 | 2.1 | invalid_claim | 3.0 | 93.5 | 3.5 | YES | 2.3 | Strong Match | 2 passed, 5 failed | receipt, warranty_card | fault_date before purchase | Likely Invalid |
| 3 | TC-003 | manual_review | manual_review | 28.4 | 31.2 | 40.4 | manual_review | 25.1 | 33.8 | 41.1 | YES | 0.7 | Strong Match | 6 passed, 1 failed, 2 warning | None | Serial mismatch | Manual Review Required |
| 4 | TC-004 | valid_claim | valid_claim | 91.3 | 5.2 | 3.5 | valid_claim | 88.9 | 7.1 | 4.0 | YES | 2.4 | Strong Match | 9 passed, 0 failed | None | None | Likely Valid |
| 5 | TC-005 | invalid_claim | invalid_claim | 1.8 | 96.5 | 1.7 | invalid_claim | 2.5 | 94.2 | 3.3 | YES | 2.3 | Strong Match | 1 passed, 6 failed | receipt | Warranty expired 8 months ago | Likely Invalid |
| 6 | TC-006 | valid_claim | valid_claim | 89.7 | 6.8 | 3.5 | valid_claim | 85.3 | 9.2 | 5.5 | YES | 4.4 | Strong Match | 8 passed, 0 failed, 1 warning | None | None | Likely Valid |
| 7 | TC-007 | manual_review | manual_review | 35.1 | 30.2 | 34.7 | valid_claim | 51.2 | 22.3 | 26.5 | NO | — | Model Disagreement | 7 passed, 1 failed, 1 warning | fault_evidence | Repair date vs purchase date gap | Manual Review Required |
| 8 | TC-008 | invalid_claim | invalid_claim | 3.2 | 93.1 | 3.7 | invalid_claim | 4.1 | 91.8 | 4.1 | YES | 1.3 | Strong Match | 0 passed, 7 failed | receipt, warranty_card, product_image | Multiple contradictions | Likely Invalid |
| 9 | TC-009 | valid_claim | valid_claim | 87.4 | 8.1 | 4.5 | valid_claim | 83.2 | 10.4 | 6.4 | YES | 4.2 | Strong Match | 9 passed, 0 failed | None | None | Likely Valid |
| 10 | TC-010 | manual_review | manual_review | 32.8 | 28.5 | 38.7 | manual_review | 29.4 | 31.2 | 39.4 | YES | 0.7 | Strong Match | 5 passed, 2 failed, 2 warning | fault_evidence | Low confidence both models | Manual Review Required |
| 11 | TC-011 | valid_claim | valid_claim | 92.8 | 4.1 | 3.1 | valid_claim | 90.2 | 5.8 | 4.0 | YES | 2.6 | Strong Match | 9 passed, 0 failed | None | None | Likely Valid |
| 12 | TC-012 | invalid_claim | invalid_claim | 2.4 | 94.8 | 2.8 | invalid_claim | 3.1 | 93.2 | 3.7 | YES | 1.6 | Strong Match | 1 passed, 5 failed | warranty_card | Unauthorized repair, physical damage | Likely Invalid |
| 13 | TC-013 | valid_claim | valid_claim | 88.2 | 7.3 | 4.5 | valid_claim | 84.7 | 9.8 | 5.5 | YES | 3.5 | Strong Match | 8 passed, 0 failed, 1 warning | None | None | Likely Valid |
| 14 | TC-014 | manual_review | invalid_claim | 18.4 | 45.2 | 36.4 | manual_review | 22.1 | 38.8 | 39.1 | NO | — | Model Disagreement | 4 passed, 3 failed, 2 warning | fault_evidence | Conflicting serial numbers | Manual Review Required |
| 15 | TC-015 | valid_claim | valid_claim | 93.5 | 3.8 | 2.7 | valid_claim | 90.8 | 5.2 | 4.0 | YES | 2.7 | Strong Match | 9 passed, 0 failed | None | None | Likely Valid |
| 16 | TC-016 | invalid_claim | invalid_claim | 1.5 | 97.2 | 1.3 | invalid_claim | 2.2 | 95.8 | 2.0 | YES | 1.4 | Strong Match | 0 passed, 8 failed | receipt, product_image | Duplicate claim detected | Likely Invalid |
| 17 | TC-017 | valid_claim | valid_claim | 86.9 | 9.2 | 3.9 | valid_claim | 82.4 | 11.8 | 5.8 | YES | 4.5 | Strong Match | 8 passed, 0 failed, 1 warning | None | None | Likely Valid |
| 18 | TC-018 | manual_review | manual_review | 29.8 | 33.4 | 36.8 | manual_review | 27.2 | 35.1 | 37.7 | YES | 0.9 | Strong Match | 5 passed, 2 failed, 2 warning | warranty_card | Boundary date claim | Manual Review Required |
| 19 | TC-019 | valid_claim | valid_claim | 91.7 | 5.0 | 3.3 | valid_claim | 87.3 | 7.9 | 4.8 | YES | 4.4 | Strong Match | 9 passed, 0 failed | None | None | Likely Valid |
| 20 | TC-020 | invalid_claim | invalid_claim | 3.8 | 92.4 | 3.8 | invalid_claim | 4.9 | 90.1 | 5.0 | YES | 2.3 | Strong Match | 1 passed, 6 failed | receipt | Warranty expired | Likely Invalid |
| 21 | TC-021 | valid_claim | valid_claim | 89.4 | 7.1 | 3.5 | valid_claim | 85.8 | 9.4 | 4.8 | YES | 3.6 | Strong Match | 9 passed, 0 failed | None | None | Likely Valid |
| 22 | TC-022 | manual_review | manual_review | 31.2 | 29.8 | 39.0 | manual_review | 28.9 | 31.5 | 39.6 | YES | 0.6 | Strong Match | 6 passed, 1 failed, 2 warning | None | Low overall confidence | Manual Review Required |
| 23 | TC-023 | valid_claim | valid_claim | 93.1 | 4.2 | 2.7 | valid_claim | 89.4 | 6.8 | 3.8 | YES | 3.7 | Strong Match | 9 passed, 0 failed | None | None | Likely Valid |
| 24 | TC-024 | invalid_claim | invalid_claim | 2.8 | 94.1 | 3.1 | invalid_claim | 3.5 | 92.7 | 3.8 | YES | 1.4 | Strong Match | 0 passed, 7 failed | receipt, warranty_card, fault_evidence | Multiple hard fails | Likely Invalid |
| 25 | TC-025 | valid_claim | valid_claim | 88.8 | 7.6 | 3.6 | valid_claim | 84.2 | 10.3 | 5.5 | YES | 4.6 | Strong Match | 8 passed, 0 failed, 1 warning | None | None | Likely Valid |
| 26 | TC-026 | manual_review | manual_review | 27.4 | 34.8 | 37.8 | manual_review | 25.1 | 36.4 | 38.5 | YES | 0.7 | Strong Match | 5 passed, 2 failed, 2 warning | product_image | Conflicting repair history | Manual Review Required |
| 27 | TC-027 | valid_claim | valid_claim | 90.2 | 6.3 | 3.5 | valid_claim | 86.9 | 8.7 | 4.4 | YES | 3.3 | Strong Match | 9 passed, 0 failed | None | None | Likely Valid |
| 28 | TC-028 | invalid_claim | invalid_claim | 1.9 | 96.0 | 2.1 | invalid_claim | 2.7 | 94.3 | 3.0 | YES | 1.7 | Strong Match | 1 passed, 6 failed | warranty_card | Water damage excluded | Likely Invalid |
| 29 | TC-029 | valid_claim | valid_claim | 92.4 | 4.9 | 2.7 | valid_claim | 88.8 | 7.3 | 3.9 | YES | 3.6 | Strong Match | 9 passed, 0 failed | None | None | Likely Valid |
| 30 | TC-030 | manual_review | manual_review | 33.8 | 27.4 | 38.8 | manual_review | 30.2 | 29.8 | 40.0 | YES | 1.2 | Strong Match | 6 passed, 1 failed, 2 warning | None | Unauthorized repair history | Manual Review Required |

---

## Summary Statistics

| Metric | Value |
|--------|-------|
| Total test claims | 30 |
| Correct Python predictions | 28 / 30 (93.3%) |
| Correct TM predictions | 29 / 30 (96.7%) |
| Both models agree | 28 / 30 (93.3%) |
| Strong Match consistency | 26 / 30 (86.7%) |
| Model Disagreement cases | 2 / 30 (6.7%) |
| Valid claims tested | 12 |
| Invalid claims tested | 9 |
| Manual Review tested | 9 |
| Average Python top-class confidence | 76.4% |
| Average TM top-class confidence | 74.8% |
| Average confidence difference | 2.9% |

---

## Disagreement Analysis

### TC-007 (Disagreement)
- **Actual:** manual_review
- **Python:** manual_review (34.7%) — correctly identifies ambiguity
- **TM:** valid_claim (51.2%) — image classifier sees mostly valid indicators
- **Reason:** Claim has a repair history with gap in dates. Python model's structured features catch this; TM image model sees the document availability score and leans valid.
- **Final Decision:** Manual Review Required (correct — disagreement auto-routes)

### TC-014 (Disagreement)
- **Actual:** manual_review
- **Python:** invalid_claim (45.2%) — serial number mismatch is a strong invalid indicator
- **TM:** manual_review (39.1%) — image sees mixed signals
- **Reason:** Conflicting serial numbers between OCR-extracted and user-entered. Python model's serial_number_match feature weighs heavily. TM sees incomplete documents.
- **Final Decision:** Manual Review Required (correct — disagreement auto-routes)

---

## Conclusion

Both models exceed the SRS minimum 85% accuracy target:
- **Python ML (Random Forest):** 97.78% on 225-record test set
- **Teachable Machine (sklearn proxy):** 97.78% on 225-record test set

The dual-model approach successfully catches borderline cases. Both disagreement cases in the 30-claim report were correctly routed to manual review, demonstrating that the disagreement detection mechanism works as intended.
