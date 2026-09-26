"""
AssureX Custom Template Tags & Filters
Load in templates with: {% load assurex_tags %}
"""
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


# ── Filters ──────────────────────────────────────────────────────

@register.filter
def replace(value, args):
    """
    Replace substring in a string.
    Usage:  {{ value|replace:"old,new" }}
    """
    try:
        old, new = args.split(',', 1)
        return str(value).replace(old, new)
    except (ValueError, AttributeError):
        return value


@register.filter
def replace_underscore(value):
    """Replace underscores with spaces. Usage: {{ value|replace_underscore }}"""
    try:
        return str(value).replace('_', ' ')
    except AttributeError:
        return value


@register.filter
def split(value, delimiter=','):
    """Split a string. Usage: {{ value|split:"," }}"""
    try:
        return str(value).split(delimiter)
    except AttributeError:
        return []


@register.filter
def get_item(dictionary, key):
    """Get a dict value by key. Usage: {{ mydict|get_item:key }}"""
    try:
        return dictionary.get(key)
    except AttributeError:
        return None


@register.filter
def prediction_label(value):
    """
    Convert prediction slug to human-readable label.
    'valid_claim' → 'Valid'
    'invalid_claim' → 'Invalid'
    'manual_review' → 'Manual Review'
    """
    mapping = {
        'valid_claim':   'Valid',
        'invalid_claim': 'Invalid',
        'manual_review': 'Manual Review',
    }
    return mapping.get(str(value), str(value).replace('_', ' ').title())


@register.filter
def consistency_label(value):
    """Convert consistency slug to readable label."""
    mapping = {
        'strong_match':     'Strong Match',
        'acceptable_match': 'Acceptable Match',
        'weak_match':       'Weak Match',
        'model_disagreement': 'Model Disagreement',
        'uncertain_result': 'Uncertain Result',
    }
    return mapping.get(str(value), str(value).replace('_', ' ').title())


@register.filter
def decision_label(value):
    """Convert final_decision slug to readable label."""
    mapping = {
        'likely_valid':   'Likely Valid',
        'likely_invalid': 'Likely Invalid',
        'manual_review':  'Manual Review Required',
        'pending':        'Pending',
    }
    return mapping.get(str(value), str(value).replace('_', ' ').title())


@register.filter
def doc_type_label(value):
    """Convert doc_type slug to readable label."""
    mapping = {
        'purchase_receipt': 'Purchase Receipt',
        'warranty_card':    'Warranty Card',
        'product_image':    'Product Image',
        'fault_evidence':   'Fault Evidence',
        'repair_report':    'Repair Report',
        'serial_photo':     'Serial Number Photo',
        'diagnostic':       'Diagnostic Report',
        'other':            'Other',
    }
    return mapping.get(str(value), str(value).replace('_', ' ').title())


@register.filter
def damage_label(value):
    mapping = {
        'physical':      'Physical Damage',
        'electrical':    'Electrical Fault',
        'mechanical':    'Mechanical Failure',
        'software':      'Software Issue',
        'manufacturing': 'Manufacturing Defect',
        'water':         'Water Damage',
        'overheating':   'Overheating',
        'battery':       'Battery Issue',
        'display':       'Display Problem',
        'other':         'Other',
    }
    return mapping.get(str(value), str(value).replace('_', ' ').title())


# ── Simple tags ───────────────────────────────────────────────────

@register.simple_tag
def prediction_badge(prediction):
    """Render a Bootstrap badge for a prediction value."""
    color = {
        'valid_claim':   'success',
        'invalid_claim': 'danger',
        'manual_review': 'warning',
    }.get(prediction, 'secondary')
    label = prediction_label(prediction)
    return mark_safe(
        f'<span class="badge bg-{color}-subtle text-{color} rounded-pill">{label}</span>'
    )


@register.simple_tag
def consistency_badge(status):
    color = {
        'strong_match':      'success',
        'acceptable_match':  'info',
        'weak_match':        'warning',
        'model_disagreement':'danger',
        'uncertain_result':  'secondary',
    }.get(status, 'secondary')
    label = consistency_label(status)
    return mark_safe(
        f'<span class="badge bg-{color}-subtle text-{color}">{label}</span>'
    )
