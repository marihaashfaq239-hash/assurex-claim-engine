# AssureX — Video Demo Test Checklist

**Video record karne se pehle yeh sab ek baar khud test karo.**
Har cheez check mark karo — tab video banao.

---

## PART 1 — Setup (Record se pehle karo, screen pe nahi)

- [ ] Server chal raha hai: `py manage.py runserver`
- [ ] Browser mein `http://127.0.0.1:8000` khul raha hai
- [ ] Landing page complete dikh raha hai (navbar, hero, animations)
- [ ] Demo accounts kaam kar rahe hain (seed_data.py chala hua hai)
- [ ] ML model files exist karte hain: `model/python_model/assurex_model.pkl`
- [ ] TM model file exist karti hai: `model/teachable_machine/sklearn_tm_model.pkl`

---

## PART 2 — Landing Page Check

- [ ] Navbar dikh raha hai (AssureX logo, links, Sign In button)
- [ ] Hero section: h1 text visible hai "Warranty Claims, Decided by AI"
- [ ] Floating badges dikh rahe hain (98.2%, 99.1%, 4, 23)
- [ ] Stats bar mein counter animation chal rahi hai
- [ ] Marquee ticker scroll ho raha hai
- [ ] Feature cards hover pe 3D tilt ho rahi hai
- [ ] Process section visible hai
- [ ] AI metrics section visible hai
- [ ] Sign In button kaam kar raha hai

---

## PART 3 — Customer Flow Test

**3.1 Register as Customer**
- [ ] `/accounts/register/` khulja hai
- [ ] Form bhar ke submit karo
  - Name: Ali Hassan
  - Email: ali@test.com
  - Password: Test@1234
  - Role: Customer
- [ ] Register ke baad Customer Dashboard pe redirect ho gaya
- [ ] Welcome notification dikh rahi hai

**3.2 Product Register**
- [ ] Products → Register Product
- [ ] Fill karo:
  - Product: Samsung Split AC
  - Brand: Samsung
  - Category: Air Conditioner
  - Model: AR18TV3QAWK
  - Serial: AC-TEST-2024-001
  - Purchase Date: 2024-01-15
  - Price: 150000
  - Retailer: Hafeez Centre Lahore
  - Warranty: 24 months
- [ ] Submit karo
- [ ] Product list mein dikh raha hai
- [ ] Warranty auto-ban gayi — Warranties mein dekho

**3.3 Submit Claim — 4 Steps**

*Step 1 — Fault Details:*
- [ ] Claims → Submit New Claim
- [ ] Product: Samsung Split AC (select karo)
- [ ] Fault Description: "AC is not cooling properly, compressor making noise"
- [ ] Damage Type: Mechanical Failure
- [ ] Fault Date: last week ki date
- [ ] Next karo

*Step 2 — Document Upload:*
- [ ] Purchase Receipt upload karo (koi bhi image file)
- [ ] OCR result dikh raha hai (extracted fields)
- [ ] Product Image upload karo
- [ ] Next karo

*Step 3 — Repair History:*
- [ ] Skip karo (Next dabao) — no previous repairs

*Step 4 — Review & Submit:*
- [ ] Summary dikh rahi hai
- [ ] Contradictions section check karo
- [ ] Submit Claim dabao
- [ ] "Claim submitted, AI evaluating" message aaya
- [ ] Claim detail page pe redirect hua

**3.4 Claim Result Dekhna**
- [ ] Claim detail page pe jao
- [ ] Python ML prediction visible hai (with confidence %)
- [ ] Teachable Machine prediction visible hai
- [ ] Model Consistency Status dikh rahi hai
- [ ] Final Decision dikh rahi hai
- [ ] Notifications bell mein update aaya

---

## PART 4 — Reviewer Flow Test

- [ ] Logout karo
- [ ] Login as: `reviewer@assurex.com` / `Reviewer@123`
- [ ] Reviewer Dashboard khul gaya
- [ ] Review Queue mein claims dikh rahe hain (agar manual review ka claim hai)
- [ ] Kisi claim pe click karo → full detail dikh rahi hai
- [ ] AI results, OCR data, rule results sab visible hain
- [ ] Approve button kaam karta hai
- [ ] Comments box mein kuch likho phir submit karo
- [ ] Claim status "Approved" ho gaya

---

## PART 5 — Admin Flow Test

- [ ] Logout karo
- [ ] Login as: `admin@assurex.com` / `Admin@123`
- [ ] Admin Dashboard: stats dikh rahi hain
  - Total Claims
  - Valid / Invalid / Manual counts
  - Recent claims table
- [ ] User Management: users list dikh rahi hai
- [ ] AI Thresholds:
  - [ ] Page khul rahi hai
  - [ ] Confidence threshold ka value dikh raha hai
  - [ ] Change karke save karo (e.g., 0.70 → 0.65)
  - [ ] Success message aaya
- [ ] Analytics page: charts render ho rahe hain
- [ ] Export Reports: CSV download ho raha hai
- [ ] Audit Logs: actions log dikh rahe hain
- [ ] Monitoring: duplicate/disagreement counts dikh rahe hain

---

## PART 6 — Employee Flow Test

- [ ] Logout karo
- [ ] Login as: `employee@assurex.com` / `Employee@123`
- [ ] Employee Dashboard khul gaya
- [ ] Customer Search: ali@test.com search karo
- [ ] Customer ka product dikh raha hai
- [ ] "Create Claim" button kaam karta hai

---

## PART 7 — Special Scenarios for Video

Yeh 4 scenarios video mein zaroor dikhao:

**Scenario A — OCR Live Demo**
- [ ] Step 2 pe receipt upload karo
- [ ] OCR automatically fields extract kare — camera pe focus karo
- [ ] "OCR extraction complete" message aaye

**Scenario B — AI Pipeline Result**
- [ ] Claim submit ke baad detail page pe jao
- [ ] Python ML confidence scores screen pe clearly dikhao
- [ ] TM confidence scores dikhao
- [ ] Model Consistency Status explain karo (e.g., "Strong Match — 4% difference")
- [ ] Final Decision highlighted hai

**Scenario C — Admin Threshold Change (Surprise Modification Ready)**
- [ ] Admin → AI Thresholds
- [ ] Confidence threshold 0.70 se 0.65 karo
- [ ] "Updated" message aaye
- [ ] Explain: "Ab 65% se upar confidence wale claims automatically decide honge"

**Scenario D — Duplicate Claim Detection**
- [ ] Same receipt file dobara upload karo kisi doosre claim mein
- [ ] "Warning: document used in another claim" message aaye

---

## PART 8 — Deployment URL Check (Railway)

- [ ] `https://your-app.up.railway.app` browser mein khul raha hai
- [ ] Landing page load ho rahi hai
- [ ] Login kaam kar raha hai
- [ ] Claim submit ho raha hai

---

## VIDEO STRUCTURE (Follow karo)

```
00:00 - 01:00  Introduction
               "AssureX ek AI-powered warranty claim management system hai..."
               Problem: manual verification slow, inconsistent decisions
               Solution: dual AI models + rule engine

01:00 - 01:45  Architecture
               Diagram dikhao: Django → Python ML + TM → Rule Engine → Decision

01:45 - 03:30  LIVE DEMO — Customer
               Landing page → Register → Product Register → Submit Claim
               OCR pe focus karo (Step 2)
               Final AI result dikhao

03:30 - 04:30  Reviewer
               Login → Queue → Full claim detail → Approve

04:30 - 05:30  Admin
               Dashboard stats → AI Threshold change → Analytics charts

05:30 - 06:30  AI Pipeline Explain
               Code briefly dikhao (evaluator.py)
               "Python ML 98.2%, TM 99.1% — dono match karte hain"
               Confusion matrix dikhao from training report

06:30 - 07:30  Railway Live URL
               Browser mein live site open karo
               Same demo quick run

07:30 - 08:00  Wrap up
               "All 50 SRS requirements complete hain"
               GitHub link mention karo
```

---

## BEFORE RECORDING — Final Check

- [ ] Browser zoom 100% hai
- [ ] Incognito window use karo (no saved data)
- [ ] Screen recording software ready (OBS / Loom / Xbox Game Bar Win+G)
- [ ] Microphone test kiya
- [ ] No other windows open
- [ ] Terminal hidden hai (unless code dikhana ho)
- [ ] Network connection stable hai
