"""
AssureX — Policy Loader
Reads all JSON policy files from policies/ and seeds the WarrantyPolicy database table.

Run:
    py database/load_policies.py
"""
import os, sys, django, json
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assurex.settings.development')
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
django.setup()

from apps.warranties.models import WarrantyPolicy
from apps.products.models import ProductCategory

POLICIES_DIR = Path(__file__).resolve().parent.parent / 'policies'

def load_all():
    print('=== Loading Warranty Policies ===')
    for path in sorted(POLICIES_DIR.glob('policy_*.json')):
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        cat_name = data.get('product_category', 'General')
        cat, _   = ProductCategory.objects.get_or_create(
            name=cat_name, defaults={'description': f'{cat_name} products'}
        )

        obj, created = WarrantyPolicy.objects.update_or_create(
            name=data['name'],
            defaults={
                'product_category':           cat,
                'standard_duration_months':   data['coverage'].get('standard_duration_months', 12),
                'extended_duration_months':   data['coverage'].get('extended_duration_months', 0),
                'claim_reporting_period_days':data['coverage'].get('claim_reporting_period_days', 14),
                'covered_faults':             data.get('covered_faults', []),
                'exclusions':                 data.get('exclusions', []),
                'mandatory_documents':        data.get('mandatory_documents', []),
                'authorized_repair_required': data.get('repair_conditions', {}).get('authorized_repair_required', True),
                'max_repair_count':           data.get('repair_conditions', {}).get('max_repair_count', 2),
                'replacement_allowed':        data.get('repair_conditions', {}).get('replacement_allowed', False),
                'hard_fail_rules':            data.get('hard_fail_rules', []),
                'warning_rules':              data.get('warning_rules', []),
                'manual_review_rules':        data.get('manual_review_rules', []),
                'policy_file':                path.name,
                'is_active':                  True,
            }
        )
        action = 'Created' if created else 'Updated'
        print(f'  [{action}] {obj.name}')

    print(f'\nTotal policies loaded: {WarrantyPolicy.objects.count()}')

if __name__ == '__main__':
    load_all()
