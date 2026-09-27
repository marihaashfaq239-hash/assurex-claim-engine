"""
AssureX — Demo Data Seeder
Run: python manage.py shell < scripts/seed_demo_data.py
  OR: python manage.py runscript seed_demo_data  (if django-extensions installed)

Creates:
  - 4 Products (owned by customer@assurex.com)
  - 4 Warranties (one per product)
  - 4 Claims (submitted, with different statuses & decisions)
"""

import django, os, sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assurex.settings.development')
django.setup()

from datetime import date, timedelta
from django.utils import timezone
from apps.accounts.models import User
from apps.products.models import Product, ProductCategory
from apps.warranties.models import Warranty, WarrantyPolicy
from apps.claims.models import Claim

# ── helpers ──────────────────────────────────────────────────────
def ok(msg):  print(f'  ✅  {msg}')
def skip(msg): print(f'  ⏭️   {msg}')

TODAY       = date.today()
customer    = User.objects.get(email='customer@assurex.com')
admin_user  = User.objects.get(email='admin@assurex.com')

cat_smartphone = ProductCategory.objects.get(name='Smartphone')
cat_laptop     = ProductCategory.objects.get(name='Laptop')
cat_tv         = ProductCategory.objects.get(name='Television')
cat_ac         = ProductCategory.objects.get(name='Air Conditioner')

policy_smartphone = WarrantyPolicy.objects.filter(product_category=cat_smartphone).first()
policy_laptop     = WarrantyPolicy.objects.filter(product_category=cat_laptop).first()
policy_general    = WarrantyPolicy.objects.get(name='Default Warranty Policy')

print('\n══════════════════════════════════════════')
print('  AssureX Demo Data Seeder')
print('══════════════════════════════════════════')

# ═══════════════════════════════════════════════════════════════
# PRODUCTS
# ═══════════════════════════════════════════════════════════════
print('\n── Products ─────────────────────────────')

products_data = [
    dict(
        product_name='Galaxy S24 Ultra',
        brand='Samsung',
        category=cat_smartphone,
        model_number='SM-S928B',
        serial_number='SN-SAM-S24U-00142',
        purchase_date=TODAY - timedelta(days=180),
        purchase_price=299999,
        retailer='Hafeez Centre Lahore',
        purchase_city='Lahore',
        warranty_duration_months=12,
        notes='Purchased from authorized Samsung dealer.',
    ),
    dict(
        product_name='ThinkPad X1 Carbon Gen 12',
        brand='Lenovo',
        category=cat_laptop,
        model_number='21KC000EPK',
        serial_number='SN-LEN-X1C-00389',
        purchase_date=TODAY - timedelta(days=290),
        purchase_price=399999,
        retailer='TechZone Karachi',
        purchase_city='Karachi',
        warranty_duration_months=24,
        notes='Extended warranty purchased at time of sale.',
    ),
    dict(
        product_name='OLED C3 65-inch',
        brand='LG',
        category=cat_tv,
        model_number='OLED65C3PSA',
        serial_number='SN-LG-C3-00755',
        purchase_date=TODAY - timedelta(days=400),
        purchase_price=549999,
        retailer='Best Electronics Islamabad',
        purchase_city='Islamabad',
        warranty_duration_months=12,
        notes='Smart TV with webOS.',
    ),
    dict(
        product_name='Inverter AC 1.5 Ton',
        brand='Gree',
        category=cat_ac,
        model_number='GS-18FITH5S',
        serial_number='SN-GRE-AC-01122',
        purchase_date=TODAY - timedelta(days=500),
        purchase_price=159999,
        retailer='Al-Fatah Electronics',
        purchase_city='Lahore',
        warranty_duration_months=24,
        notes='Inverter AC with 5-year compressor warranty.',
    ),
]

products = []
for pd in products_data:
    obj, created = Product.objects.get_or_create(
        serial_number=pd['serial_number'],
        defaults={**pd, 'owner': customer}
    )
    products.append(obj)
    if created:
        ok(f'Product created: {obj.brand} {obj.product_name}')
    else:
        skip(f'Product already exists: {obj.brand} {obj.product_name}')

# ═══════════════════════════════════════════════════════════════
# WARRANTIES
# ═══════════════════════════════════════════════════════════════
print('\n── Warranties ───────────────────────────')

warranties_data = [
    dict(
        product=products[0],
        policy=policy_smartphone,
        warranty_type='standard',
        warranty_provider='Samsung Pakistan',
        start_date=products[0].purchase_date,
        expiry_date=products[0].purchase_date + timedelta(days=365),
        coverage_description='Covers manufacturing defects, electrical faults, and display issues. Excludes physical damage and water damage.',
        status='active',
    ),
    dict(
        product=products[1],
        policy=policy_laptop,
        warranty_type='extended',
        warranty_provider='Lenovo Pakistan',
        start_date=products[1].purchase_date,
        expiry_date=products[1].purchase_date + timedelta(days=730),
        coverage_description='Covers hardware defects, battery replacement, keyboard and trackpad issues. Excludes accidental damage.',
        status='active',
    ),
    dict(
        product=products[2],
        policy=policy_general,
        warranty_type='standard',
        warranty_provider='LG Electronics Pakistan',
        start_date=products[2].purchase_date,
        expiry_date=products[2].purchase_date + timedelta(days=365),
        coverage_description='Covers panel defects, electrical faults, and software issues. Excludes physical damage.',
        status='expired',
    ),
    dict(
        product=products[3],
        policy=policy_general,
        warranty_type='standard',
        warranty_provider='Gree Pakistan',
        start_date=products[3].purchase_date,
        expiry_date=products[3].purchase_date + timedelta(days=730),
        coverage_description='Full parts and labor. 5-year compressor warranty. Excludes refrigerant refill and filter cleaning.',
        status='active',
    ),
]

warranties = []
for wd in warranties_data:
    obj, created = Warranty.objects.get_or_create(
        product=wd['product'],
        warranty_type=wd['warranty_type'],
        defaults=wd
    )
    warranties.append(obj)
    if created:
        ok(f'Warranty created: {obj.product.brand} {obj.product.product_name} ({obj.status})')
    else:
        skip(f'Warranty already exists: {obj.product.brand} {obj.product.product_name}')

# ═══════════════════════════════════════════════════════════════
# CLAIMS
# ═══════════════════════════════════════════════════════════════
print('\n── Claims ───────────────────────────────')

claims_data = [
    # Claim 1 — Smartphone, Approved (Likely Valid)
    dict(
        claimant=customer,
        product=products[0],
        warranty=warranties[0],
        fault_date=TODAY - timedelta(days=10),
        fault_description=(
            'The display started showing green flickering lines on the right side of the screen. '
            'The issue appears intermittently at first but is now permanent. No physical damage or drops occurred.'
        ),
        damage_type='display',
        fault_location='Display — Right edge',
        additional_notes='Issue started after a software update.',
        status='approved',
        final_decision='likely_valid',
        decision_reason=(
            'AI models both predict valid claim with high confidence. '
            'Display flickering is a known manufacturing defect covered under warranty. '
            'No unauthorized repairs or physical damage detected.'
        ),
        python_prediction='valid_claim',
        python_confidence_valid=0.9456,
        python_confidence_invalid=0.0312,
        python_confidence_manual=0.0232,
        tm_prediction='valid_claim',
        tm_confidence_valid=0.9811,
        tm_confidence_invalid=0.0121,
        tm_confidence_manual=0.0068,
        confidence_difference=0.0355,
        model_consistency_status='strong_match',
        rules_passed=10,
        rules_failed=0,
        rules_warning=1,
        submission_date=timezone.now() - timedelta(days=9),
        evaluated_at=timezone.now() - timedelta(days=9),
    ),
    # Claim 2 — Laptop, Manual Review
    dict(
        claimant=customer,
        product=products[1],
        warranty=warranties[1],
        fault_date=TODAY - timedelta(days=20),
        fault_description=(
            'Laptop battery drains completely within 45 minutes of unplugging even at low usage. '
            'Battery health shows 61% in system diagnostics. Charging port also seems loose.'
        ),
        damage_type='battery',
        fault_location='Battery / Charging port',
        additional_notes='Battery health dropped very quickly — had the laptop for less than a year.',
        status='manual',
        final_decision='manual_review',
        decision_reason=(
            'Models agree on manual review due to mixed signals: battery degradation '
            'could be usage-pattern related or a manufacturing defect. '
            'Reviewer should inspect charging port damage classification.'
        ),
        python_prediction='manual_review',
        python_confidence_valid=0.3812,
        python_confidence_invalid=0.2544,
        python_confidence_manual=0.3644,
        tm_prediction='manual_review',
        tm_confidence_valid=0.3120,
        tm_confidence_invalid=0.2980,
        tm_confidence_manual=0.3900,
        confidence_difference=0.0692,
        model_consistency_status='acceptable_match',
        rules_passed=8,
        rules_failed=1,
        rules_warning=2,
        submission_date=timezone.now() - timedelta(days=19),
        evaluated_at=timezone.now() - timedelta(days=19),
    ),
    # Claim 3 — TV, Rejected (Likely Invalid — warranty expired)
    dict(
        claimant=customer,
        product=products[2],
        warranty=warranties[2],
        fault_date=TODAY - timedelta(days=5),
        fault_description=(
            'TV panel has developed a large dark patch on the lower left corner. '
            'The area is about 15cm x 10cm and is progressively getting larger.'
        ),
        damage_type='display',
        fault_location='Panel — Lower left quadrant',
        additional_notes='No physical impact or damage visible on the screen.',
        status='rejected',
        final_decision='likely_invalid',
        decision_reason=(
            'Warranty expired 35 days before the reported fault date. '
            'Rule engine hard-fail: warranty_expired_at_fault. '
            'Claim falls outside coverage period.'
        ),
        python_prediction='invalid_claim',
        python_confidence_valid=0.0644,
        python_confidence_invalid=0.8922,
        python_confidence_manual=0.0434,
        tm_prediction='invalid_claim',
        tm_confidence_valid=0.0512,
        tm_confidence_invalid=0.9144,
        tm_confidence_manual=0.0344,
        confidence_difference=0.0222,
        model_consistency_status='strong_match',
        rules_passed=7,
        rules_failed=2,
        rules_warning=1,
        submission_date=timezone.now() - timedelta(days=4),
        evaluated_at=timezone.now() - timedelta(days=4),
    ),
    # Claim 4 — AC, Submitted (under evaluation)
    dict(
        claimant=customer,
        product=products[3],
        warranty=warranties[3],
        fault_date=TODAY - timedelta(days=3),
        fault_description=(
            'Air conditioner is not cooling effectively. Temperature reads 28°C even after running for 2 hours '
            'on maximum cooling. Unusual rattling sound is also coming from the outdoor unit.'
        ),
        damage_type='mechanical',
        fault_location='Outdoor unit — Compressor',
        additional_notes='Issue started during the recent heatwave. No prior repairs.',
        status='evaluation',
        final_decision='pending',
        decision_reason='',
        python_prediction='',
        python_confidence_valid=None,
        python_confidence_invalid=None,
        python_confidence_manual=None,
        tm_prediction='',
        tm_confidence_valid=None,
        tm_confidence_invalid=None,
        tm_confidence_manual=None,
        confidence_difference=None,
        model_consistency_status='',
        rules_passed=0,
        rules_failed=0,
        rules_warning=0,
        submission_date=timezone.now() - timedelta(days=2),
        evaluated_at=None,
    ),
]

for cd in claims_data:
    existing = Claim.objects.filter(
        claimant=cd['claimant'],
        product=cd['product'],
        damage_type=cd['damage_type'],
        fault_date=cd['fault_date'],
    ).first()
    if existing:
        skip(f'Claim already exists: {existing.claim_reference} — {existing.product.product_name}')
        continue

    claim = Claim(**cd)
    claim.save()
    # auto-generate claim_reference
    if not claim.claim_reference:
        claim.claim_reference = f'CLM-{claim.pk:07d}'
        claim.save(update_fields=['claim_reference'])
    ok(f'Claim created: {claim.claim_reference} — {claim.product.product_name} [{claim.status.upper()}]')

print('\n══════════════════════════════════════════')
print('  Seeding complete!')
print('  Login: customer@assurex.com')
print('══════════════════════════════════════════\n')
