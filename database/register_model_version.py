"""
Register trained ML model version in the database.
Run after train_model.py completes.
"""
import os, sys, django, json
from pathlib import Path
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assurex.settings.development')
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
django.setup()

from apps.claims.models import ModelVersion

MODEL_DIR = Path(__file__).resolve().parent.parent / 'model' / 'python_model'

def register():
    # Load comparison report
    comp_path = MODEL_DIR / 'model_comparison.json'
    if not comp_path.exists():
        print('ERROR: model_comparison.json not found. Run train_model.py first.')
        return

    with open(comp_path) as f:
        comp = json.load(f)

    best = comp['best_model']
    test_acc = comp['models'][best].get('test_accuracy', 0)

    # Deactivate old versions
    ModelVersion.objects.filter(model_type='python_ml').update(is_active=False)

    v, created = ModelVersion.objects.get_or_create(
        model_type='python_ml',
        version_name='v1.0',
        defaults={
            'description': f'Best model: {best}. Test accuracy: {test_acc}%',
            'file_path':   str(MODEL_DIR / 'assurex_model.pkl'),
            'accuracy':    test_acc,
            'is_active':   True,
            'trained_at':  datetime.now(),
        }
    )
    if not created:
        v.accuracy = test_acc
        v.is_active = True
        v.description = f'Best model: {best}. Test accuracy: {test_acc}%'
        v.save()

    print(f'[+] Python ML model version registered: v1.0 | Accuracy: {test_acc}% | Active: True')

    # Register TM placeholder
    ModelVersion.objects.get_or_create(
        model_type='teachable_machine',
        version_name='v1.0',
        defaults={
            'description': 'Google Teachable Machine — awaiting GTM export',
            'file_path':   'model/teachable_machine/',
            'is_active':   True,
        }
    )
    print('[+] Teachable Machine placeholder version registered.')
    print('\nAll done!')

if __name__ == '__main__':
    register()
