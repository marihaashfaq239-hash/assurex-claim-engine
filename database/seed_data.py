"""
AssureX — Database Seed Script
Run with: python manage.py shell < database/seed_data.py
Or: python database/seed_data.py  (after setting DJANGO_SETTINGS_MODULE)

Creates:
  - Default admin user
  - Product categories
  - System configuration defaults
  - Sample warranty policies (loaded from policies/ JSON files)
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assurex.settings.development')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
django.setup()

from apps.accounts.models import User
from apps.products.models import ProductCategory
from apps.administrator.models import SystemConfiguration


def create_admin():
    if not User.objects.filter(email='admin@assurex.com').exists():
        user = User.objects.create_superuser(
            email='admin@assurex.com',
            password='Admin@123',
            first_name='System',
            last_name='Admin',
        )
        print(f'[+] Admin created: {user.email}')
    else:
        print('[=] Admin already exists')


def create_product_categories():
    categories = [
        ('Air Conditioner',   'bi-wind',           'AC units and climate control'),
        ('Refrigerator',      'bi-thermometer',    'Refrigerators and freezers'),
        ('Washing Machine',   'bi-arrow-repeat',   'Washers and dryers'),
        ('Television',        'bi-tv',             'TVs and display devices'),
        ('Smartphone',        'bi-phone',          'Mobile phones and tablets'),
        ('Laptop',            'bi-laptop',         'Laptops and notebooks'),
        ('Microwave',         'bi-lightning',      'Microwave ovens'),
        ('Generator',         'bi-plug',           'Generators and power backup'),
        ('Water Heater',      'bi-droplet-half',   'Geysers and water heaters'),
        ('Small Appliance',   'bi-box-seam',       'Irons, blenders, fans, etc.'),
    ]
    for name, icon, desc in categories:
        obj, created = ProductCategory.objects.get_or_create(
            name=name,
            defaults={'icon': icon, 'description': desc}
        )
        if created:
            print(f'  [+] Category: {name}')


def create_system_config():
    defaults = [
        ('confidence_threshold_min',   '0.70',   'float', 'Minimum confidence to auto-decide'),
        ('strong_match_max_diff',       '5.0',    'float', 'Max % diff for Strong Match'),
        ('acceptable_match_max_diff',   '15.0',   'float', 'Max % diff for Acceptable Match'),
        ('weak_match_max_diff',         '25.0',   'float', 'Max % diff for Weak Match'),
        ('auto_approve_confidence',     '0.92',   'float', 'Auto-approve if both models ≥ this'),
        ('auto_reject_confidence',      '0.92',   'float', 'Auto-reject if both models ≥ this'),
        ('warranty_expiry_alert_days',  '30',     'int',   'Days before expiry to alert'),
        ('claim_reporting_period_days', '14',     'int',   'Max days to report after fault'),
        ('max_file_size_mb',            '5',      'int',   'Max document upload size in MB'),
        ('max_claims_per_product',      '3',      'int',   'Max claims per product'),
    ]
    for key, value, vtype, desc in defaults:
        obj, created = SystemConfiguration.objects.get_or_create(
            key=key,
            defaults={'value': value, 'value_type': vtype, 'description': desc}
        )
        if created:
            print(f'  [+] Config: {key} = {value}')


def create_demo_users():
    demo_users = [
        {
            'email': 'customer@assurex.com', 'password': 'Customer@123',
            'first_name': 'Ahmed', 'last_name': 'Khan', 'role': User.CUSTOMER,
        },
        {
            'email': 'employee@assurex.com', 'password': 'Employee@123',
            'first_name': 'Sara', 'last_name': 'Ali', 'role': User.EMPLOYEE,
        },
        {
            'email': 'reviewer@assurex.com', 'password': 'Reviewer@123',
            'first_name': 'Bilal', 'last_name': 'Hassan', 'role': User.REVIEWER,
        },
    ]
    for data in demo_users:
        if not User.objects.filter(email=data['email']).exists():
            User.objects.create_user(**data)
            print(f"  [+] Demo user: {data['email']} ({data['role']})")
        else:
            print(f"  [=] Demo user exists: {data['email']}")


if __name__ == '__main__':
    print('=== AssureX Database Seeder ===')
    print('\n[1] Creating admin user...')
    create_admin()
    print('\n[2] Creating product categories...')
    create_product_categories()
    print('\n[3] Creating system configuration defaults...')
    create_system_config()
    print('\n[4] Creating demo users...')
    create_demo_users()
    print('\n=== Seeding complete! ===')
    print('\nDemo accounts:')
    print('  Admin:    admin@assurex.com    / Admin@123')
    print('  Customer: customer@assurex.com / Customer@123')
    print('  Employee: employee@assurex.com / Employee@123')
    print('  Reviewer: reviewer@assurex.com / Reviewer@123')
