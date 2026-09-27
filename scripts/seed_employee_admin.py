"""
AssureX — Employee & Admin Demo Data Seeder
Usage: python manage.py shell < scripts/seed_employee_admin.py
"""
from datetime import date, timedelta
from django.utils import timezone
from apps.accounts.models import User
from apps.products.models import Product, ProductCategory
from apps.warranties.models import Warranty, WarrantyPolicy
from apps.claims.models import Claim

TODAY    = date.today()
employee = User.objects.get(email='employee@assurex.com')

# ── 3 extra demo customers ────────────────────────────────────────
def get_or_create_customer(email, first, last, phone, city):
    u, created = User.objects.get_or_create(email=email, defaults=dict(
        first_name=first, last_name=last, role='customer',
        phone=phone, city=city, is_active=True, is_verified=True))
    if created:
        u.set_password('Demo@1234')
        u.save()
        print(f'  + customer: {u.get_full_name()} ({email})')
    return u

c2 = get_or_create_customer('ali.raza@demo.com',   'Ali',   'Raza',  '03001234567', 'Karachi')
c3 = get_or_create_customer('fatima.noor@demo.com','Fatima','Noor',  '03211234567', 'Lahore')
c4 = get_or_create_customer('usman.tariq@demo.com','Usman', 'Tariq', '03451234567', 'Islamabad')

# ── Categories & Policies ─────────────────────────────────────────
cat_phone  = ProductCategory.objects.get(name='Smartphone')
cat_laptop = ProductCategory.objects.get(name='Laptop')
cat_wash   = ProductCategory.objects.get(name='Washing Machine')
cat_fridge = ProductCategory.objects.get(name='Refrigerator')
pol_phone  = WarrantyPolicy.objects.filter(product_category=cat_phone).first()
pol_laptop = WarrantyPolicy.objects.filter(product_category=cat_laptop).first()
pol_gen    = WarrantyPolicy.objects.get(name='Default Warranty Policy')

# ── Products ──────────────────────────────────────────────────────
def gp(sn, owner, name, brand, cat, model, days, price, shop, city, months):
    p, created = Product.objects.get_or_create(serial_number=sn, defaults=dict(
        owner=owner, product_name=name, brand=brand, category=cat,
        model_number=model, purchase_date=TODAY-timedelta(days=days),
        purchase_price=price, retailer=shop, purchase_city=city,
        warranty_duration_months=months))
    if created:
        print(f'  + product: {brand} {name}')
    return p

pr_a = gp('SN-OPP-RN11-0221', c2, 'Reno 11 Pro',            'OPPO',  cat_phone,  'CPH2599',    120, 89999,  'Metro Electronics Karachi', 'Karachi',   12)
pr_b = gp('SN-HP-EB840-0432',  c3, 'EliteBook 840 G11',      'HP',    cat_laptop, 'A37QBET',     95, 329999, 'Laptop Store Lahore',       'Lahore',    12)
pr_c = gp('SN-HAI-WM8-0678',   c4, 'Automatic Washer 8kg',   'Haier', cat_wash,   'HWM120-1678S',60, 79999,  'Daraz Online',              'Islamabad', 24)
pr_d = gp('SN-PEL-FR20-0911',  c2, 'Jumbo Fridge 20CF',      'PEL',   cat_fridge, 'PRGD-22350', 200, 119999, 'Al-Karam Electronics',      'Karachi',   24)

# ── Warranties ────────────────────────────────────────────────────
def gw(product, wtype, provider, pol, days, desc, status):
    w, created = Warranty.objects.get_or_create(product=product, warranty_type=wtype, defaults=dict(
        policy=pol, warranty_provider=provider,
        start_date=product.purchase_date,
        expiry_date=product.purchase_date+timedelta(days=days),
        coverage_description=desc, status=status))
    if created:
        print(f'  + warranty: {product.brand} ({status})')
    return w

w_a = gw(pr_a, 'standard', 'OPPO Pakistan',  pol_phone,  365, 'Covers manufacturing defects. Excludes water damage.', 'active')
w_b = gw(pr_b, 'standard', 'HP Pakistan',    pol_laptop, 365, 'Covers hardware defects. Excludes physical damage.',   'active')
w_c = gw(pr_c, 'standard', 'Haier Pakistan', pol_gen,    730, 'Full parts and labor. Excludes misuse.',               'active')
w_d = gw(pr_d, 'standard', 'PEL Pakistan',   pol_gen,    730, 'Covers all parts and compressor.',                     'active')

# ── Claim helper ──────────────────────────────────────────────────
def mc(claimant, product, fault_date, fault_desc, damage_type, fault_loc,
       notes, status, final_decision, decision_reason,
       py_pred, py_v, py_i, py_m, tm_pred, tm_v, tm_i, tm_m,
       conf_diff, consistency, r_pass, r_fail, r_warn,
       sub_date, eval_date, submitted_by=None, warranty=None):

    if Claim.objects.filter(claimant=claimant, product=product, fault_date=fault_date).exists():
        print(f'  skip: {product.brand} {product.product_name}')
        return
    c = Claim(
        claimant=claimant, submitted_by=submitted_by,
        product=product, warranty=warranty,
        fault_date=fault_date, fault_description=fault_desc,
        damage_type=damage_type, fault_location=fault_loc,
        additional_notes=notes, status=status,
        final_decision=final_decision, decision_reason=decision_reason,
        python_prediction=py_pred,
        python_confidence_valid=py_v, python_confidence_invalid=py_i, python_confidence_manual=py_m,
        tm_prediction=tm_pred,
        tm_confidence_valid=tm_v, tm_confidence_invalid=tm_i, tm_confidence_manual=tm_m,
        confidence_difference=conf_diff, model_consistency_status=consistency,
        rules_passed=r_pass, rules_failed=r_fail, rules_warning=r_warn,
        submission_date=sub_date, evaluated_at=eval_date,
    )
    c.save()
    print(f'  + claim: {c.claim_reference} — {product.brand} {product.product_name} [{status.upper()}]')

# ════════════════════════════════════════════════════════════════
# EMPLOYEE-SUBMITTED CLAIMS
# ════════════════════════════════════════════════════════════════
print('\n── Employee Claims ─────────────────────')

# E1 — OPPO front camera, Approved
mc(c2, pr_a, TODAY-timedelta(days=8),
   'Front camera stopped working completely. No image or video capture. Rear camera still functional. No drop or water.',
   'manufacturing','Front camera module','Customer confirmed with service center — hardware fault.',
   'approved','likely_valid','Both AI models strongly agree: front camera manufacturing defect covered under warranty.',
   'valid_claim',0.9122,0.0544,0.0334, 'valid_claim',0.8944,0.0712,0.0344,
   0.0178,'strong_match',10,0,1,
   timezone.now()-timedelta(days=7), timezone.now()-timedelta(days=7),
   submitted_by=employee, warranty=w_a)

# E2 — HP keyboard, Approved
mc(c3, pr_b, TODAY-timedelta(days=14),
   'G, H, and spacebar keys stopped responding suddenly. No liquid spill, no physical impact observed.',
   'manufacturing','Keyboard','No damage signs. Pure internal hardware failure.',
   'approved','likely_valid','Strong AI agreement: keyboard hardware fault is a manufacturing defect under warranty.',
   'valid_claim',0.8834,0.0766,0.0400, 'valid_claim',0.9201,0.0544,0.0255,
   0.0367,'strong_match',11,0,0,
   timezone.now()-timedelta(days=13), timezone.now()-timedelta(days=13),
   submitted_by=employee, warranty=w_b)

# E3 — Haier washer, Manual Review (model disagreement)
mc(c4, pr_c, TODAY-timedelta(days=5),
   'Extreme vibration and loud noise during spin cycle. Wash cycle taking nearly 2 hours per load.',
   'mechanical','Drum / Motor','No overloading observed. Issue appeared after 2 months of use.',
   'manual','manual_review','Python predicts valid, Vision flags manual. Drum noise could be installation or defect — manual review needed.',
   'valid_claim',0.5122,0.2344,0.2534, 'manual_review',0.3200,0.2900,0.3900,
   0.1922,'weak_match',8,1,2,
   timezone.now()-timedelta(days=4), timezone.now()-timedelta(days=4),
   submitted_by=employee, warranty=w_c)

# E4 — PEL fridge, Under Evaluation
mc(c2, pr_d, TODAY-timedelta(days=2),
   'Fridge not maintaining temperature. Fresh compartment reads 12C instead of 4C. Freezer still working.',
   'mechanical','Compressor / Thermostat','Customer noticed food spoiling faster. Issue started 2 days ago.',
   'evaluation','pending','',
   '',None,None,None, '',None,None,None,
   None,'',0,0,0,
   timezone.now()-timedelta(days=1), None,
   submitted_by=employee, warranty=w_d)

# E5 — HP laptop display, Submitted today
mc(c3, pr_b, TODAY-timedelta(days=1),
   'Display intermittent flickering. Screen goes black for 2-3 seconds randomly throughout the day.',
   'display','Display panel','Flickering started yesterday. No physical damage or drops.',
   'submitted','pending','',
   '',None,None,None, '',None,None,None,
   None,'',0,0,0,
   timezone.now(), None,
   submitted_by=employee, warranty=w_b)

# ════════════════════════════════════════════════════════════════
# ADDITIONAL CLAIMS — spread over last 7 days (for admin trend chart)
# ════════════════════════════════════════════════════════════════
print('\n── Extra Claims for Admin Trend Chart ──')

# Get existing customer & products
customer = User.objects.get(email='customer@assurex.com')
p_sam = Product.objects.get(serial_number='SN-SAM-S24U-00142')
p_len = Product.objects.get(serial_number='SN-LEN-X1C-00389')
w_sam = Warranty.objects.get(product=p_sam, warranty_type='standard')
w_len = Warranty.objects.get(product=p_len, warranty_type='extended')

# Day -6: one claim
mc(customer, p_sam, TODAY-timedelta(days=25),
   'Charging port intermittently not recognized by cable. Needs multiple attempts to start charging.',
   'electrical','Charging port','Issue started after 6 months of use. No physical damage to port.',
   'approved','likely_valid','Both models agree: charging port fault is a manufacturing defect.',
   'valid_claim',0.8755,0.0844,0.0401, 'valid_claim',0.9012,0.0644,0.0344,
   0.0257,'strong_match',10,0,1,
   timezone.now()-timedelta(days=6), timezone.now()-timedelta(days=6))

# Day -4: one claim
mc(c2, pr_a, TODAY-timedelta(days=30),
   'Speaker producing crackling distorted audio during calls and media playback.',
   'manufacturing','Speaker module','All apps affected. External speaker also tested — same issue.',
   'rejected','likely_invalid','Warranty expired at time of fault by 12 days.',
   'invalid_claim',0.1200,0.8100,0.0700, 'invalid_claim',0.0900,0.8800,0.0300,
   0.0700,'strong_match',7,2,1,
   timezone.now()-timedelta(days=4), timezone.now()-timedelta(days=4))

# Day -3: one claim (duplicate flag)
mc(c2, pr_d, TODAY-timedelta(days=35),
   'Fridge making continuous humming noise. Temperature fluctuating between 6-14C.',
   'mechanical','Compressor','Second claim for similar issue on same product.',
   'manual','manual_review','Flagged as potential duplicate. Manual review required to verify.',
   'manual_review',0.3500,0.3200,0.3300, 'manual_review',0.3100,0.3400,0.3500,
   0.0400,'uncertain_result',6,2,3,
   timezone.now()-timedelta(days=3), timezone.now()-timedelta(days=3))

# Day -2: one claim
mc(c4, pr_c, TODAY-timedelta(days=40),
   'Water leaking from the bottom of the machine during wash cycle.',
   'mechanical','Door seal / Drum','Small puddle forming under machine. No visible cracks on drum.',
   'approved','likely_valid','Clear manufacturing defect — door seal failure covered under warranty.',
   'valid_claim',0.8922,0.0644,0.0434, 'valid_claim',0.9100,0.0544,0.0356,
   0.0178,'strong_match',10,0,1,
   timezone.now()-timedelta(days=2), timezone.now()-timedelta(days=2))

# Day -1: one claim
mc(c3, pr_b, TODAY-timedelta(days=45),
   'Laptop overheating severely under normal load. Fan running at full speed constantly. CPU throttling.',
   'overheating','CPU / Cooling system','Thermal paste dried up or cooling fan failing.',
   'manual','manual_review','Models weakly agree on manual review. Overheating could be maintenance or defect.',
   'manual_review',0.4200,0.2600,0.3200, 'manual_review',0.3800,0.2900,0.3300,
   0.0400,'acceptable_match',8,1,2,
   timezone.now()-timedelta(days=1), timezone.now()-timedelta(days=1))

print('\n══════════════════════════════════════')
print('Seeding complete!')
print(f'Total claims in DB: {Claim.objects.count()}')
print(f'Employee claims   : {Claim.objects.filter(submitted_by=employee).count()}')
print('══════════════════════════════════════')
