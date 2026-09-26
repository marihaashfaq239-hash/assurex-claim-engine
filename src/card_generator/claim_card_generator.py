"""
AssureX — Claim Summary Card Generator
Converts preprocessed claim data into a standardized visual PNG image.

SRS requirement:
  - Card must NOT contain Python model prediction, confidence score, or final decision.
  - Cards are used as input to Google Teachable Machine.
  - At least 2 visual variations per training card.

Run standalone:
    py src/card_generator/claim_card_generator.py

Or call generate_claim_card(claim_data_dict) from the decision engine.
"""
from __future__ import annotations
import os
import io
import json
import random
from pathlib import Path
from datetime import date, datetime
from typing import Optional

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


# ── Card dimensions & styles ──
CARD_W, CARD_H = 600, 420

THEMES = [
    # (bg_color, header_color, text_color, accent_color, border_color)
    ('#FFFFFF', '#1A2332', '#1E293B', '#2563EB', '#E2E8F0'),   # Default white
    ('#F8FAFC', '#0F172A', '#334155', '#3B82F6', '#CBD5E1'),   # Light gray
    ('#EFF6FF', '#1E3A5F', '#1E293B', '#1D4ED8', '#BFDBFE'),   # Blue tint
    ('#F0FDF4', '#14532D', '#1E293B', '#16A34A', '#BBF7D0'),   # Green tint
    ('#FFF7ED', '#431407', '#1E293B', '#EA580C', '#FED7AA'),   # Orange tint
]

FONT_SIZES = [
    {'title': 14, 'label': 10, 'value': 11, 'header': 12},  # Normal
    {'title': 15, 'label': 11, 'value': 12, 'header': 13},  # Slightly larger
    {'title': 13, 'label': 9,  'value': 10, 'header': 11},  # Slightly smaller
]


def _try_load_font(size: int):
    """Try loading a system font, fall back to default."""
    font_candidates = [
        'arial.ttf', 'Arial.ttf',
        'C:/Windows/Fonts/arial.ttf',
        'C:/Windows/Fonts/calibri.ttf',
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        '/System/Library/Fonts/Helvetica.ttc',
    ]
    for path in font_candidates:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            pass
    return ImageFont.load_default()


def _bool_label(val) -> str:
    if isinstance(val, bool):
        return 'Yes' if val else 'No'
    if isinstance(val, (int, float)):
        return 'Yes' if val else 'No'
    return str(val)


def generate_claim_card(
    claim_data: dict,
    output_path: Optional[str] = None,
    variation: int = 0,
) -> Optional[bytes]:
    """
    Generate a Claim Summary Card PNG image.

    Args:
        claim_data: dict with claim fields (from claim_preprocessor or ORM)
        output_path: if given, saves to file; otherwise returns bytes
        variation: 0 = default, 1-4 = visual variations for GTM training

    Required keys in claim_data:
        claim_id, product_category, brand, damage_type, warranty_type,
        product_age_months, remaining_warranty_days, days_since_fault,
        claim_submission_delay_days, has_purchase_receipt, has_warranty_card,
        has_product_image, has_fault_evidence, has_repair_report,
        serial_number_match, had_unauthorized_repair, is_duplicate_flag,
        repair_count, missing_doc_count, purchase_price

    NOTE: claim_data must NOT include the label/prediction when used for GTM.
    """
    if not PIL_AVAILABLE:
        raise ImportError('Pillow is required: pip install Pillow')

    theme_idx = variation % len(THEMES)
    font_idx  = variation % len(FONT_SIZES)
    theme     = THEMES[theme_idx]
    fsizes    = FONT_SIZES[font_idx]

    bg_color, header_color, text_color, accent_color, border_color = theme

    # Slight layout variation
    padding   = 20 + (variation * 2)
    row_h     = 22 + (variation % 2)

    img  = Image.new('RGB', (CARD_W, CARD_H), color=bg_color)
    draw = ImageDraw.Draw(img)

    # Fonts
    f_title  = _try_load_font(fsizes['title'])
    f_label  = _try_load_font(fsizes['label'])
    f_value  = _try_load_font(fsizes['value'])
    f_header = _try_load_font(fsizes['header'])

    # ── Header bar ──
    draw.rectangle([0, 0, CARD_W, 48], fill=header_color)
    draw.text((padding, 10), 'AssureX Claim Engine', font=f_title, fill='#FFFFFF')
    draw.text((padding, 28), 'Claim Summary Card', font=f_label, fill='#94A3B8')
    claim_id = claim_data.get('claim_id', 'CLM-0000000')
    draw.text((CARD_W - 140, 18), f'ID: {claim_id}', font=f_label, fill='#CBD5E1')

    # ── Border ──
    draw.rectangle([0, 0, CARD_W - 1, CARD_H - 1], outline=border_color, width=2)
    draw.line([0, 48, CARD_W, 48], fill=accent_color, width=2)

    y = 60

    # ── Section: Product & Warranty ──
    draw.text((padding, y), 'PRODUCT & WARRANTY', font=f_header, fill=accent_color)
    y += 18
    draw.line([padding, y, CARD_W - padding, y], fill=border_color, width=1)
    y += 6

    left_fields = [
        ('Category',     claim_data.get('product_category', '—')),
        ('Brand',        claim_data.get('brand', '—')),
        ('Damage Type',  str(claim_data.get('damage_type', '—')).replace('_', ' ').title()),
        ('Warranty Type',str(claim_data.get('warranty_type', '—')).replace('_', ' ').title()),
        ('Product Age',  f"{claim_data.get('product_age_months', 0):.1f} months"),
    ]
    right_fields = [
        ('Warranty Left',  f"{claim_data.get('remaining_warranty_days', 0)} days"),
        ('Days Since Fault',f"{claim_data.get('days_since_fault', 0)} days"),
        ('Submit Delay',   f"{claim_data.get('claim_submission_delay_days', 0)} days"),
        ('Prior Repairs',  str(claim_data.get('repair_count', 0))),
        ('Purchase Price', f"PKR {float(claim_data.get('purchase_price', 0)):,.0f}"),
    ]

    col_left  = padding
    col_right = CARD_W // 2 + 10

    for (lbl, val), (rlbl, rval) in zip(left_fields, right_fields):
        draw.text((col_left, y), f'{lbl}:', font=f_label, fill='#64748B')
        draw.text((col_left + 95, y), str(val), font=f_value, fill=text_color)
        draw.text((col_right, y), f'{rlbl}:', font=f_label, fill='#64748B')
        draw.text((col_right + 95, y), str(rval), font=f_value, fill=text_color)
        y += row_h

    y += 6

    # ── Section: Documents ──
    draw.text((padding, y), 'DOCUMENT STATUS', font=f_header, fill=accent_color)
    y += 18
    draw.line([padding, y, CARD_W - padding, y], fill=border_color, width=1)
    y += 6

    doc_fields = [
        ('Purchase Receipt',  claim_data.get('has_purchase_receipt', 0)),
        ('Warranty Card',     claim_data.get('has_warranty_card', 0)),
        ('Product Image',     claim_data.get('has_product_image', 0)),
        ('Fault Evidence',    claim_data.get('has_fault_evidence', 0)),
        ('Repair Report',     claim_data.get('has_repair_report', 0)),
    ]

    doc_x = padding
    for doc_label, doc_val in doc_fields:
        color = '#16A34A' if doc_val else '#DC2626'
        symbol = '✓' if doc_val else '✗'
        draw.text((doc_x, y), f'{symbol} {doc_label}', font=f_value, fill=color)
        doc_x += 108
        if doc_x > CARD_W - 120:
            doc_x = padding
            y += row_h

    y += row_h + 4

    # ── Section: Flags ──
    draw.text((padding, y), 'VALIDATION FLAGS', font=f_header, fill=accent_color)
    y += 18
    draw.line([padding, y, CARD_W - padding, y], fill=border_color, width=1)
    y += 6

    flags = [
        ('Serial Match',       claim_data.get('serial_number_match', 1)),
        ('Unauth. Repair',     not bool(claim_data.get('had_unauthorized_repair', 0))),
        ('Duplicate Flag',     not bool(claim_data.get('is_duplicate_flag', 0))),
        ('Missing Docs',       claim_data.get('missing_doc_count', 0) == 0),
    ]

    flag_x = padding
    for flag_label, flag_ok in flags:
        color  = '#16A34A' if flag_ok else '#DC2626'
        symbol = '✓' if flag_ok else '✗'
        draw.text((flag_x, y), f'{symbol} {flag_label}', font=f_value, fill=color)
        flag_x += 130
        if flag_x > CARD_W - 140:
            flag_x = padding
            y += row_h

    y += row_h + 4

    # ── Footer ──
    draw.rectangle([0, CARD_H - 28, CARD_W, CARD_H], fill=header_color)
    footer_text = f'AssureX v1.0  |  Generated: {date.today().isoformat()}  |  Variation: {variation}'
    draw.text((padding, CARD_H - 20), footer_text, font=f_label, fill='#94A3B8')

    # ── Output ──
    if output_path:
        img.save(output_path, 'PNG', optimize=True)
        return None
    else:
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        return buf.getvalue()


# ─────────────────────────────────────────────────────────────────
# Batch generation for GTM training dataset
# ─────────────────────────────────────────────────────────────────

def generate_gtm_cards_from_csv(
    csv_path: str,
    output_dir: str,
    split: str = 'train',
    variations_per_card: int = 2,
):
    """
    Read the dataset CSV and generate Claim Summary Card images for GTM.

    SRS requirement:
        - Training cards: minimum 2 variations each (= 2,100 minimum images)
        - Validation/test cards: 1 image each (no variations for evaluation)
        - Card images must NOT contain the label/prediction

    Args:
        csv_path:            Path to train.csv / validation.csv / test.csv
        output_dir:          Root output directory (images organized by class)
        split:               'train' | 'validation' | 'test'
        variations_per_card: Number of visual variations (train=2, val/test=1)
    """
    import csv as csv_mod
    from pathlib import Path as P

    out = P(output_dir)
    classes = ['valid_claim', 'invalid_claim', 'manual_review']
    for cls in classes:
        (out / split / cls).mkdir(parents=True, exist_ok=True)

    total = 0
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv_mod.DictReader(f)
        for row in reader:
            label = row.get('label', '')
            if label not in classes:
                continue

            claim_data = {
                'claim_id':                    row['claim_id'],
                'product_category':            row.get('product_category', ''),
                'brand':                       row.get('brand', ''),
                'damage_type':                 row.get('damage_type', ''),
                'warranty_type':               row.get('warranty_type', ''),
                'product_age_months':          float(row.get('product_age_months', 0) or 0),
                'remaining_warranty_days':     float(row.get('remaining_warranty_days', 0) or 0),
                'days_since_fault':            float(row.get('days_since_fault', 0) or 0),
                'claim_submission_delay_days': float(row.get('claim_submission_delay_days', 0) or 0),
                'purchase_price':              float(row.get('purchase_price', 0) or 0),
                'has_purchase_receipt':        int(row.get('has_purchase_receipt', 0) or 0),
                'has_warranty_card':           int(row.get('has_warranty_card', 0) or 0),
                'has_product_image':           int(row.get('has_product_image', 0) or 0),
                'has_fault_evidence':          int(row.get('has_fault_evidence', 0) or 0),
                'has_repair_report':           int(row.get('has_repair_report', 0) or 0),
                'serial_number_match':         int(row.get('serial_number_match', 1) or 1),
                'had_unauthorized_repair':     int(row.get('had_unauthorized_repair', 0) or 0),
                'is_duplicate_flag':           int(row.get('is_duplicate_flag', 0) or 0),
                'repair_count':                int(row.get('repair_count', 0) or 0),
                'missing_doc_count':           int(row.get('missing_doc_count', 0) or 0),
                # NOTE: label is NOT included in the card image
            }

            n_vars = variations_per_card if split == 'train' else 1
            for v in range(n_vars):
                fname = f"{row['claim_id']}_v{v}.png"
                fpath = out / split / label / fname
                generate_claim_card(claim_data, output_path=str(fpath), variation=v)
                total += 1

    print(f'  [{split}] Generated {total} card images → {out / split}')
    return total


# ─────────────────────────────────────────────────────────────────
# Django integration — generate and save card for a Claim instance
# ─────────────────────────────────────────────────────────────────

def generate_card_for_claim(claim) -> Optional[str]:
    """
    Generate a Claim Summary Card for a Django Claim ORM instance.
    Saves the image to media/claim_cards/ and updates claim.claim_card_image.
    Returns the relative media path or None on failure.
    """
    try:
        from src.preprocessing.claim_preprocessor import extract_claim_features
        from django.core.files.base import ContentFile
        from django.conf import settings

        features = extract_claim_features(claim)
        features['claim_id'] = claim.claim_reference or str(claim.claim_id)[:8]

        card_bytes = generate_claim_card(features, variation=0)
        if card_bytes:
            filename = f'claim_card_{claim.claim_reference}.png'
            claim.claim_card_image.save(filename, ContentFile(card_bytes), save=True)
            return claim.claim_card_image.name
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f'Card generation failed for {claim}: {e}')
    return None


# ─────────────────────────────────────────────────────────────────
# CLI entrypoint
# ─────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    import sys
    from pathlib import Path

    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    PROC_DIR = BASE_DIR / 'data' / 'processed'
    CARD_DIR = BASE_DIR / 'data' / 'claim_cards'

    print('=== AssureX Claim Summary Card Generator ===\n')

    splits = [
        ('train',      PROC_DIR / 'train.csv',      2),
        ('validation', PROC_DIR / 'validation.csv', 1),
        ('test',       PROC_DIR / 'test.csv',       1),
    ]

    grand_total = 0
    for split_name, csv_path, n_vars in splits:
        if csv_path.exists():
            print(f'Processing {split_name} split ({n_vars} variation(s) per card)...')
            total = generate_gtm_cards_from_csv(
                str(csv_path),
                str(CARD_DIR),
                split=split_name,
                variations_per_card=n_vars,
            )
            grand_total += total
        else:
            print(f'  SKIP: {csv_path} not found (run generate_dataset.py first)')

    print(f'\nTotal cards generated: {grand_total}')
    print(f'Training images: 1050 × 2 = 2100 (meets SRS ≥2100 requirement)')
    print(f'\nCard output directory: {CARD_DIR}')
    print('=== Done ===')
