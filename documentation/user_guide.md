# AssureX Claim Engine — User Guide

**Version:** 1.0 · **Date:** September 2026
**Team:** Muhammad Hunain · Mariha Ashfaq · Owais Ahmed · Muhammad Daniyal
**Competition:** TechWiz 7 — Aptech Computer Education

---

## Table of Contents

1. [Getting Started](#1-getting-started)
2. [Customer Guide](#2-customer-guide)
3. [Employee Guide](#3-service-center-employee-guide)
4. [Reviewer Guide](#4-claim-reviewer-guide)
5. [Administrator Guide](#5-administrator-guide)

---

## 1. Getting Started

### 1.1 Accessing the Application

Open your browser and navigate to:
- **Local:** `http://127.0.0.1:8000`
- **Production:** `https://assurex.up.railway.app`

> 📸 **[Screenshot: Landing Page]** — `screenshots/00_landing.png`

### 1.2 User Roles

| Role | Description | Access Level |
|------|-------------|--------------|
| **Customer** | Product owners who submit warranty claims | Own products & claims only |
| **Employee** | Service center staff who submit claims on behalf of customers | Customer lookup + claim creation |
| **Reviewer** | Claim reviewers who handle manual review queue | All claims in manual review |
| **Administrator** | System administrators | Full system access |

### 1.3 Registering an Account

1. Click **"Start Free Trial"** on the landing page
2. Select your role: **Customer** or **Service Center Employee**
3. Fill in: First Name, Last Name, Email, Password
4. Click **"Create Account"**
5. You will be redirected to your role-specific dashboard

> 📸 **[Screenshot: Register Page]** — `screenshots/02_register.png`

### 1.4 Logging In

1. Click **"Get Started"** or **"Sign In"** on the landing page
2. Enter your **Email** and **Password**
3. Click **"Sign In"**
4. You will be redirected to your dashboard based on your role

> 📸 **[Screenshot: Login Page]** — `screenshots/01_login.png`

### 1.5 Demo Accounts

| Role | Email | Password |
|------|-------|----------|
| Administrator | admin@assurex.com | Admin@123 |
| Customer | customer@assurex.com | Customer@123 |
| Employee | employee@assurex.com | Employee@123 |
| Reviewer | reviewer@assurex.com | Reviewer@123 |

---

## 2. Customer Guide

### 2.1 Dashboard Overview

After login, the Customer Dashboard shows:
- **Registered Products** — total count
- **Active Warranties** — count with expiry info
- **Pending Claims** — claims under review
- **Approved Claims** — successfully resolved claims
- **Recent Claims** — last 5 claims with status
- **Registered Products** — quick list with "Claim" button

> 📸 **[Screenshot: Customer Dashboard]** — `screenshots/03_customer_dashboard.png`

---

### 2.2 Registering a Product

**Navigation:** Sidebar → Products & Warranty → **Register Product**

**Steps:**
1. Click **"Register Product"** in the sidebar
2. Fill in the product details:
   - **Product Name** (e.g., Samsung Galaxy S24 Ultra)
   - **Brand** (e.g., Samsung)
   - **Category** (e.g., Smartphone)
   - **Model Number** (from product label)
   - **Serial Number** (unique identifier)
   - **Purchase Date**
   - **Purchase Price (PKR)**
   - **Retailer Name**
   - **Purchase City**
   - **Warranty Duration (months)**
3. Click **"Register Product"**

> 📸 **[Screenshot: Register Product Form]** — `screenshots/05_product_register.png`

**After Registration:**
- Product appears in "My Products" list
- A warranty record is automatically created
- You can now submit claims for this product

---

### 2.3 Viewing My Products

**Navigation:** Sidebar → **My Products**

The products list shows:
- Product name, brand, category
- Serial number
- Purchase date
- Warranty status (Active / Expired / Expiring Soon)
- Action buttons: View Details, Submit Claim

> 📸 **[Screenshot: Products List]** — `screenshots/04_products_list.png`

---

### 2.4 Viewing Warranties

**Navigation:** Sidebar → **My Warranties**

Each warranty shows:
- Product name and serial number
- Warranty type (Standard / Extended)
- Start date and expiry date
- Days remaining
- Coverage status (Active / Expired / Expiring in X days)

> 📸 **[Screenshot: Warranties List]** — `screenshots/06_warranties_list.png`

> ⚠️ **Warranty Expiry Alert:** If a warranty is expiring within 30 days, a yellow alert banner appears on your dashboard.

---

### 2.5 Submitting a Warranty Claim

Claim submission is a **4-step wizard**.

**Navigation:** Sidebar → Claims → **Submit New Claim** OR Dashboard → **"Submit New Claim"** button

---

#### Step 1 — Fault Details

1. Select **Product** from your registered products
2. Select **Warranty** associated with the product
3. Enter **Fault Date** — when the problem first occurred
4. Select **Damage Type** (Physical / Electrical / Mechanical / etc.)
5. Write **Fault Description** — describe the problem clearly
6. Enter **Fault Location** (optional) — e.g., "Left speaker", "Charging port"
7. Click **"Save & Continue"**

> 📸 **[Screenshot: Claim Step 1]** — `screenshots/07_claim_submit_step1.png`

---

#### Step 2 — Upload Documents

Upload supporting documents. Required documents:
- ✅ **Purchase Receipt** (PDF, JPG, PNG — max 5MB)
- ✅ **Product Image** (photo of the product)
- ✅ **Fault Evidence** (photo/video of the damage)

Optional documents:
- Warranty Card
- Repair Report
- Serial Number Photo
- Diagnostic Report

**After upload:**
- OCR automatically extracts data from receipts and warranty cards
- Extracted fields (serial number, purchase date, price) are displayed
- You can **verify and correct** extracted data

> 📸 **[Screenshot: Step 2 Documents + OCR]** — `screenshots/07_claim_submit_step1.png`

---

#### Step 3 — Repair History (Optional)

If the product has been repaired before:
1. Click **"Add Repair Record"**
2. Enter: Repair Date, Repair Center, Description, Cost
3. Check **"Authorized Service Center"** if applicable
4. Click **"Add"**

Skip this step if no prior repairs.

---

#### Step 4 — Review & Submit

Final review page shows:
- All entered claim details
- Uploaded documents list
- OCR-extracted data
- **Contradiction warnings** (if any issues detected)
- **Missing documents** warning

If everything looks correct, click **"Submit Claim"**.

> ⚠️ Once submitted, the claim cannot be edited.

> 📸 **[Screenshot: Step 4 Review]** — `screenshots/07_claim_submit_step1.png`

---

### 2.6 Tracking a Claim

**Navigation:** Sidebar → Claims → **My Claims**

The My Claims page shows all your claims with:
- Claim Reference (e.g., CLM-0000002)
- Product name
- Submission date
- Current status
- AI Decision (if evaluated)

> 📸 **[Screenshot: My Claims List]** — `screenshots/08_my_claims.png`

**Claim Status Meanings:**

| Status | Meaning |
|--------|---------|
| 🔵 Draft | Not yet submitted |
| 🟡 Submitted | Waiting for AI evaluation |
| 🟠 Under Evaluation | AI pipeline is processing |
| 🔴 Additional Info Required | More documents needed |
| 🟣 Manual Review | Human reviewer is checking |
| 🟢 Approved | Claim accepted ✅ |
| 🔴 Rejected | Claim denied ❌ |
| ⚫ Closed | Process complete |

---

### 2.7 Claim Detail View

Click any claim reference to see full details:
- Product and warranty information
- Fault details and documents
- **AI Evaluation Results:**
  - Python ML Model prediction + confidence scores
  - Google Teachable Machine prediction + confidence scores
  - Model consistency status
  - Rule engine results (11 rules)
- Final decision with explanation
- Reviewer comments (if manually reviewed)

> 📸 **[Screenshot: Claim Detail with AI Results]** — `screenshots/08_my_claims.png`

---

### 2.8 Notifications

**Navigation:** Bell icon (top right) or Sidebar → **Notifications**

You receive notifications for:
- Claim submitted confirmation
- Claim approved / rejected
- Warranty expiring soon
- Additional information requested
- Claim status changes

> 📸 **[Screenshot: Notifications]** — `screenshots/09_notifications.png`

---

### 2.9 Profile Management

**Navigation:** Top-right dropdown → **My Profile**

You can update:
- First Name, Last Name
- Phone Number
- Address, City
- Profile Picture
- Password

> 📸 **[Screenshot: Profile Page]** — `screenshots/10_profile.png`

---

## 3. Service Center Employee Guide

### 3.1 Dashboard Overview

Employee dashboard shows:
- Total Claims Created (by this employee)
- Submitted Today
- Pending Review
- Approved Claims
- Recent claims table

> 📸 **[Screenshot: Employee Dashboard]** — `screenshots/employee_dashboard.png`

---

### 3.2 Customer Search

**Navigation:** Sidebar → **Search Customer**

1. Enter customer name, email, or phone
2. Click **"Search"**
3. Select the customer from results
4. View their registered products and warranties
5. Click **"Submit Claim"** for a specific product

> This allows employees to submit claims **on behalf of customers**.

---

### 3.3 Creating a Claim for a Customer

Same 4-step wizard as customer, but:
- You select the **customer** first
- Then select their **product**
- The claim will show `submitted_by: [Employee Name]`

---

### 3.4 Viewing Created Claims

**Navigation:** Sidebar → **My Claims**

Shows all claims this employee has created, with status and AI decision.

---

## 4. Claim Reviewer Guide

### 4.1 Dashboard Overview

Reviewer dashboard shows:
- Claims in Queue (pending manual review)
- Claims Reviewed (completed)
- AI Override count
- Oldest unreviewed claim alert
- Queue preview table
- Recent decisions

> 📸 **[Screenshot: Reviewer Dashboard]** — `screenshots/21_reviewer_dashboard.png`

---

### 4.2 Review Queue

**Navigation:** Sidebar → **Review Queue**

The queue shows all claims needing manual review:
- Claim reference and product
- Customer name
- Python ML prediction
- Google Teachable Machine prediction
- Confidence difference (Δ)
- Model consistency status

> 📸 **[Screenshot: Review Queue]** — `screenshots/22_reviewer_queue.png`

---

### 4.3 Reviewing a Claim

1. Click **"Review"** on any claim in the queue
2. The review detail page shows:
   - Full claim information
   - All uploaded documents
   - OCR extracted data
   - **Python ML confidence scores** (bar chart)
   - **Google TM confidence scores** (bar chart)
   - Model comparison and consistency
   - Rule engine results (11 rules — Pass/Fail/Warning)
   - Detected contradictions
3. Make your decision:
   - ✅ **Approve** — claim is valid
   - ❌ **Reject** — claim is invalid
   - 📋 **Request More Info** — need additional documents
4. Add **reviewer comments** (required)
5. If overriding AI recommendation, tick **"Override AI"** and give reason
6. Click **"Submit Decision"**

> 📸 **[Screenshot: Review Detail Page]** — `screenshots/22_reviewer_queue.png`

---

### 4.4 Reviewed Claims

**Navigation:** Sidebar → **Reviewed Claims**

History of all claims you have reviewed with your decisions.

---

### 4.5 AI Override History

**Navigation:** Sidebar → **AI Overrides**

Shows cases where reviewer decision differed from AI recommendation — useful for audit and model improvement.

---

## 5. Administrator Guide

### 5.1 Dashboard Overview

Admin dashboard shows 10 stat cards:
- Total Claims, Likely Valid, Likely Invalid
- Manual Review, Duplicates, AI Disagreements
- Total Users, Approved, Rejected, Pending

Plus:
- Claim submissions trend chart (7 days)
- AI Decision split donut chart
- Quick action links
- Recent claims table

> 📸 **[Screenshot: Admin Dashboard]** — `screenshots/11_admin_dashboard.png`

---

### 5.2 User Management

**Navigation:** Sidebar → **User Management**

- View all users (filter by role, status)
- Search by name/email/phone
- Activate / Deactivate accounts
- Change user roles
- View user details

> 📸 **[Screenshot: User Management]** — `screenshots/12_admin_users.png`

---

### 5.3 All Claims

**Navigation:** Sidebar → **All Claims**

- View all claims in the system
- Filter by status, decision, date range, product category
- Search by reference, customer, serial number
- Click any claim to see full detail

> 📸 **[Screenshot: All Claims]** — `screenshots/13_admin_all_claims.png`

---

### 5.4 Analytics

**Navigation:** Sidebar → **Analytics**

Charts and reports on:
- Claim volume over time
- Decision distribution (Valid / Invalid / Manual)
- Model accuracy comparison
- Most common fault types
- Claim outcomes by product category

> 📸 **[Screenshot: Analytics]** — `screenshots/14_admin_analytics.png`

---

### 5.5 Model Versions

**Navigation:** Sidebar → **Model Versions**

- View registered Python ML and GTM model versions
- See accuracy per version
- Set active model version
- Register new model version after retraining

> 📸 **[Screenshot: Model Versions]** — `screenshots/15_admin_model_versions.png`

---

### 5.6 AI Thresholds

**Navigation:** Sidebar → **AI Thresholds**

Configure confidence thresholds:

| Setting | Default | Description |
|---------|---------|-------------|
| Minimum Confidence | 70% | Below this → Manual Review |
| Strong Match Threshold | 5% | Confidence diff ≤ 5% |
| Acceptable Match | 15% | Confidence diff 5–15% |
| Weak Match | 25% | Confidence diff 15–25% |
| Warranty Expiry Alert Days | 30 | Days before expiry to alert |

> 📸 **[Screenshot: AI Thresholds]** — `screenshots/16_admin_thresholds.png`

---

### 5.7 Warranty Policies

**Navigation:** Sidebar → **Warranty Policies**

- View all warranty policies per product category
- See covered faults, exclusions, mandatory documents
- Edit policy parameters (reporting period, repair limits, grace period)

> 📸 **[Screenshot: Warranty Policies]** — `screenshots/17_admin_warranty_policies.png`

---

### 5.8 Export Data

**Navigation:** Sidebar → **Reports & Export**

Export options:
- Claims CSV (all or filtered)
- Products CSV
- Analytics summary

> 📸 **[Screenshot: Export]** — `screenshots/18_admin_export.png`

---

### 5.9 Audit Logs

**Navigation:** Sidebar → **Audit Logs**

Complete audit trail of all system actions:
- User logins/logouts
- Claim submissions and decisions
- Document uploads
- AI predictions
- Reviewer overrides
- Admin actions

> 📸 **[Screenshot: Audit Logs]** — `screenshots/19_admin_audit_logs.png`

---

### 5.10 System Monitoring

**Navigation:** Sidebar → **Monitoring**

Real-time system health:
- Failed uploads
- Duplicate document alerts
- Low-confidence prediction alerts
- Model disagreement alerts
- Unusual claim activity flags

> 📸 **[Screenshot: Monitoring]** — `screenshots/20_admin_monitoring.png`

---

*AssureX Claim Engine — User Guide v1.0 · TechWiz 7 · Aptech Computer Education · 2026*
