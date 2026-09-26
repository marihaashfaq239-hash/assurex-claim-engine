# AssureX Claim Engine

**AI-Powered Warranty Claim Management System**
Category: NextWave AI and ML — Aptech Limited

---

## Overview

AssureX Claim Engine is a Python Django web application that automates warranty claim validation for manufacturers and service centers. It uses a dual-AI approach: a trained Python ML model and a Google Teachable Machine model, whose results are compared to produce a final claim recommendation.

---

## Features

- **4-role system**: Customer, Service Center Employee, Claim Reviewer, Administrator
- **Multi-step claim submission** with OCR document extraction
- **Dual AI evaluation**: Python ML (Random Forest / XGBoost / Logistic Regression) + Google Teachable Machine
- **Model comparison** with confidence score analysis
- **Warranty Rule Engine** with configurable JSON policy files
- **Final decision**: Likely Valid / Likely Invalid / Manual Review Required
- **Manual review workflow** with AI override and audit trail
- **Admin analytics** with Chart.js dashboards and CSV export

---

## Quick Start

### Prerequisites

- Python 3.11+
- Tesseract OCR ([install guide](https://github.com/UB-Mannheim/tesseract/wiki))

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/assurex-claim-engine.git
cd assurex-claim-engine

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
copy .env .env.local
# Edit .env.local with your settings

# 5. Create database
python manage.py makemigrations
python manage.py migrate

# 6. Seed initial data (categories, admin user, system config)
python database/seed_data.py

# 7. Load warranty policies
python database/load_policies.py

# 8. Collect static files
python manage.py collectstatic --noinput

# 9. Run development server
python manage.py runserver
```

Visit: http://127.0.0.1:8000

### Default Demo Accounts

| Role | Email | Password |
|---|---|---|
| Administrator | admin@assurex.com | Admin@123 |
| Customer | customer@assurex.com | Customer@123 |
| Employee | employee@assurex.com | Employee@123 |
| Reviewer | reviewer@assurex.com | Reviewer@123 |

---

## ML Model Training

```bash
# Step 1: Generate synthetic dataset (1,500 records)
python dataset_generator/generate_dataset.py

# Step 2: Train the Python ML model (3 algorithms compared)
python src/ml/train_model.py

# Step 3: Generate Claim Summary Card images for Teachable Machine
python src/card_generator/claim_card_generator.py
```

**Dataset**: 1,500 records (500 Valid / 500 Invalid / 500 Manual Review)
**Split**: 70% train (1,050) / 15% validation (225) / 15% test (225)
**GTM Images**: 2,100 training images (2 variations per card)

---

## Google Teachable Machine Setup

1. Go to [teachablemachine.withgoogle.com](https://teachablemachine.withgoogle.com)
2. Create an **Image Project**
3. Create 3 classes: `valid_claim`, `invalid_claim`, `manual_review`
4. Upload card images from `data/claim_cards/train/`
5. Train the model
6. Export as **TensorFlow SavedModel** or **TFLite**
7. Place exported model in `model/teachable_machine/`

---

## Project Structure

```
assurex/                    Django settings package
apps/
  accounts/                 Custom user model, auth, profiles
  products/                 Product registration
  warranties/               Warranty records and policies
  claims/                   Claim submission, OCR, tracking
  reviewer/                 Manual review workflow
  administrator/            Admin dashboard, analytics
  notifications/            Alerts and notifications
src/
  ocr/                      Tesseract + EasyOCR extraction
  preprocessing/            Feature engineering
  ml/                       Model training and inference
  card_generator/           Claim Summary Card image generator
  rule_engine/              Warranty rule validation
  decision_engine/          Final decision orchestrator
data/
  raw/                      Full 1,500-record dataset
  processed/                Train / validation / test splits
  claim_cards/              Generated Claim Summary Card images
model/
  python_model/             Saved sklearn model + encoders
  teachable_machine/        Exported TM model files
policies/                   Warranty policy JSON files
dataset_generator/          Synthetic data generation scripts
```

---

## Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test module
python -m pytest tests/test_rule_engine.py -v
```

---

## Deployment

### Local Development

```bash
set DJANGO_SETTINGS_MODULE=assurex.settings.development
py manage.py runserver
```

### Railway (Production) — Step by Step

**Step 1 — GitHub pe push karo**
```bash
git add .
git commit -m "feat: production deployment config"
git push origin main
```

**Step 2 — Railway project banao**
1. [railway.app](https://railway.app) pe jao → Login with GitHub
2. **New Project** → **Deploy from GitHub repo** → AssureX repo select karo
3. Railway auto-detect karega `Procfile` aur `nixpacks.toml`

**Step 3 — PostgreSQL database add karo**
1. Railway dashboard mein → **New Service** → **Database** → **PostgreSQL**
2. Railway automatically `DATABASE_URL` env var set kar dega

**Step 4 — Environment Variables set karo**
Railway project → Settings → Variables → Add these:

| Variable | Value |
|---|---|
| `DJANGO_SETTINGS_MODULE` | `assurex.settings.production` |
| `SECRET_KEY` | (generate a strong random key) |
| `DATABASE_URL` | (Railway auto-sets from PostgreSQL service) |
| `ALLOWED_HOSTS` | `your-app.up.railway.app` |
| `DEBUG` | `False` |

**Step 5 — Deploy**
1. Railway mein **Deploy** button dabao
2. Build log mein dekhte raho — `collectstatic` aur `migrate` auto-run honge
3. Deploy complete hone ke baad Railway ek URL dega: `https://your-app.up.railway.app`

**Step 6 — Seed data load karo (one time)**
Railway dashboard → project → **Shell** tab:
```bash
python database/seed_data.py
python database/load_policies.py
python database/register_model_version.py
```

**Live URL:** `https://your-app.up.railway.app`

---

## Deliverables (SRS Checklist)

- [x] Complete working web application
- [x] Public GitHub repository with meaningful commits
- [x] 1,500-record synthetic dataset (CSV + GTM images)
- [x] Python ML model (3 algorithms compared)
- [x] Google Teachable Machine model integration
- [x] Dual model comparison + confidence analysis
- [x] Warranty Rule Engine (configurable JSON policies)
- [x] Final decision engine (Valid / Invalid / Manual Review)
- [x] Manual review workflow with AI override
- [x] Admin analytics dashboard
- [x] Audit trail
- [x] Model version tracking
- [x] CSV export
- [x] Responsive UI (Bootstrap 5)
- [ ] Mandatory demonstration video *(to be recorded)*
- [ ] Minimum 2,000-word technical blog *(to be written)*
- [ ] AI_USAGE.md *(see AI_USAGE.md)*

---

## License

MIT License — see LICENSE file.
