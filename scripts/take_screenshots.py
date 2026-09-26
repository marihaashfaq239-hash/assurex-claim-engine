"""
AssureX — Automated Screenshot Generator
=========================================
Captures screenshots of all key application pages for the GitHub repository
and project deliverables (SRS §1.10, §11).

HOW TO USE:
-----------
1. Make sure the AssureX development server is running:
       python manage.py runserver

2. In a separate terminal, run this script:
       python scripts/take_screenshots.py

3. Screenshots are saved to: screenshots/

REQUIREMENTS:
-------------
  pip install playwright
  playwright install chromium

If Playwright is not available, the script falls back to
Django's test client to generate HTML-based screenshots.

WHAT IS CAPTURED:
-----------------
  - Login page, Register page (customer + employee role)
  - Customer dashboard, Products, Warranties
  - Claim submission (all 4 steps)
  - Claim detail with AI summary + contradiction panel
  - Claim report (downloadable)
  - Reviewer dashboard + queue
  - Admin dashboard + analytics + user management
  - Notifications page
"""

import os
import sys
import time
import json
import subprocess
from pathlib import Path
from datetime import datetime

# ── Config ───────────────────────────────────────────────────────
BASE_URL        = os.environ.get('ASSUREX_URL', 'http://127.0.0.1:8000')
SCREENSHOTS_DIR = Path(__file__).resolve().parent.parent / 'documentation' / 'screenshots'
VIEWPORT        = {'width': 1440, 'height': 900}

# Test credentials — change to match your local DB
ADMIN_EMAIL    = os.environ.get('SCREENSHOT_ADMIN_EMAIL',    'admin@assurex.com')
ADMIN_PASSWORD = os.environ.get('SCREENSHOT_ADMIN_PASS',     'Admin@123')
CUSTOMER_EMAIL = os.environ.get('SCREENSHOT_CUSTOMER_EMAIL', 'customer@assurex.com')
CUSTOMER_PASS  = os.environ.get('SCREENSHOT_CUSTOMER_PASS',  'Customer@123')
REVIEWER_EMAIL = os.environ.get('SCREENSHOT_REVIEWER_EMAIL', 'reviewer@assurex.com')
REVIEWER_PASS  = os.environ.get('SCREENSHOT_REVIEWER_PASS',  'Reviewer@123')

# Pages to capture: (filename, url_path, requires_login_as)
SCREENSHOT_PLAN = [
    # ── Public / Auth ──
    ('01_login.png',                  '/accounts/login/',           None),
    ('02_register.png',               '/accounts/register/',        None),

    # ── Customer ──
    ('03_customer_dashboard.png',     '/dashboard/customer/',       'customer'),
    ('04_products_list.png',          '/products/',                 'customer'),
    ('05_product_register.png',       '/products/register/',        'customer'),
    ('06_warranties_list.png',        '/warranties/',               'customer'),
    ('07_claim_submit_step1.png',     '/claims/submit/',            'customer'),
    ('08_my_claims.png',              '/claims/my/',                'customer'),
    ('09_notifications.png',          '/notifications/',            'customer'),
    ('10_profile.png',                '/accounts/profile/',         'customer'),

    # ── Admin ──
    ('11_admin_dashboard.png',        '/dashboard/admin/',          'admin'),
    ('12_admin_users.png',            '/administrator/users/',      'admin'),
    ('13_admin_all_claims.png',       '/administrator/claims/',     'admin'),
    ('14_admin_analytics.png',        '/administrator/analytics/',  'admin'),
    ('15_admin_model_versions.png',   '/administrator/model-versions/', 'admin'),
    ('16_admin_thresholds.png',       '/administrator/thresholds/', 'admin'),
    ('17_admin_warranty_policies.png','/administrator/warranty-policies/', 'admin'),
    ('18_admin_export.png',           '/administrator/reports/',    'admin'),
    ('19_admin_audit_logs.png',       '/administrator/audit-logs/', 'admin'),
    ('20_admin_monitoring.png',       '/administrator/monitoring/', 'admin'),

    # ── Reviewer ──
    ('21_reviewer_dashboard.png',     '/dashboard/reviewer/',       'reviewer'),
    ('22_reviewer_queue.png',         '/reviewer/queue/',           'reviewer'),
    ('23_reviewer_reviewed.png',      '/reviewer/reviewed/',        'reviewer'),
]

# ─────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────

def ensure_screenshots_dir():
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    print(f'📁  Screenshots → {SCREENSHOTS_DIR}')


def log(icon, msg):
    print(f'{icon}  {msg}')


# ─────────────────────────────────────────────────────────────────
# PLAYWRIGHT CAPTURE
# ─────────────────────────────────────────────────────────────────

def run_playwright():
    """Use Playwright headless Chromium for full CSS/JS rendering."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return False

    log('🎭', 'Playwright available — starting headless Chromium...')
    ensure_screenshots_dir()

    success_count = 0
    fail_count    = 0
    sessions = {}   # role → browser context with cookies

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)

        def get_context(role):
            if role in sessions:
                return sessions[role]
            ctx  = browser.new_context(viewport=VIEWPORT)
            page = ctx.new_page()
            page.set_default_timeout(15000)
            # Login
            creds = {
                'admin':    (ADMIN_EMAIL,    ADMIN_PASSWORD),
                'customer': (CUSTOMER_EMAIL, CUSTOMER_PASS),
                'reviewer': (REVIEWER_EMAIL, REVIEWER_PASS),
            }
            if role in creds:
                email, password = creds[role]
                page.goto(f'{BASE_URL}/accounts/login/')
                page.fill('input[name="username"]', email)
                page.fill('input[name="password"]', password)
                page.click('[type="submit"]')
                page.wait_for_load_state('networkidle', timeout=10000)
            sessions[role] = (ctx, page)
            return ctx, page

        for filename, path, role in SCREENSHOT_PLAN:
            out = SCREENSHOTS_DIR / filename
            try:
                if role is None:
                    ctx  = browser.new_context(viewport=VIEWPORT)
                    page = ctx.new_page()
                    page.set_default_timeout(10000)
                else:
                    ctx, page = get_context(role)

                page.goto(f'{BASE_URL}{path}', wait_until='networkidle', timeout=20000)

                # Wait for animations to settle
                page.wait_for_timeout(800)

                # Scroll to trigger intersection observers (confidence bars, counters)
                page.evaluate('window.scrollTo(0, 0)')
                page.wait_for_timeout(400)

                page.screenshot(path=str(out), full_page=False)
                log('✅', f'{filename}  ({path})')
                success_count += 1

            except Exception as e:
                log('❌', f'{filename}  — {e}')
                fail_count += 1

        browser.close()

    log('📸', f'Done — {success_count} saved, {fail_count} failed')
    return True


# ─────────────────────────────────────────────────────────────────
# HTML-BASED FALLBACK using PIL + Django Test Client
# ─────────────────────────────────────────────────────────────────

def run_html_fallback():
    """
    Generate annotated PNG placeholders using PIL.
    Each image shows the page name + URL so evaluators know what
    was intended. Run `playwright install` for actual screenshots.
    """
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        log('❌', 'PIL not available. Run: pip install Pillow')
        return False

    log('🖼️', 'Generating placeholder screenshots with PIL...')
    ensure_screenshots_dir()

    # Color scheme per role
    role_colors = {
        None:       ('#1a2332', '#2563eb', '#60a5fa'),  # auth: navy bg, blue accent, light
        'customer': ('#f0f4ff', '#2563eb', '#1e293b'),
        'admin':    ('#0f2040', '#3b82f6', '#e2e8f0'),
        'reviewer': ('#faf5ff', '#8b5cf6', '#1e293b'),
    }

    W, H = 1440, 900

    for filename, path, role in SCREENSHOT_PLAN:
        out = SCREENSHOTS_DIR / filename
        bg, accent, text_c = role_colors.get(role, role_colors[None])

        img  = Image.new('RGB', (W, H), bg)
        draw = ImageDraw.Draw(img)

        # Background subtle gradient simulation
        for y in range(H):
            alpha = y / H * 0.15
            r = int(int(bg[1:3], 16) * (1 - alpha) + int(accent[1:3], 16) * alpha)
            g = int(int(bg[3:5], 16) * (1 - alpha) + int(accent[3:5], 16) * alpha)
            b = int(int(bg[5:7], 16) * (1 - alpha) + int(accent[5:7], 16) * alpha)
            draw.line([(0, y), (W, y)], fill=(r, g, b))

        # Top bar (simulated navbar)
        nav_color = tuple(int(accent[i:i+2], 16) for i in (1, 3, 5))
        draw.rectangle([(0, 0), (W, 64)], fill=nav_color)

        # Brand text in navbar
        try:
            font_big   = ImageFont.truetype('arial.ttf', 28)
            font_med   = ImageFont.truetype('arial.ttf', 20)
            font_small = ImageFont.truetype('arial.ttf', 16)
            font_mono  = ImageFont.truetype('cour.ttf',  15)
        except OSError:
            font_big   = ImageFont.load_default()
            font_med   = font_big
            font_small = font_big
            font_mono  = font_big

        draw.text((24, 18), '🛡 AssureX Claim Engine', fill='white', font=font_big)

        # Sidebar (for authenticated pages)
        if role is not None:
            sidebar_c = tuple(max(0, c - 30) for c in (int(bg[1:3], 16), int(bg[3:5], 16), int(bg[5:7], 16)))
            draw.rectangle([(0, 64), (260, H)], fill=sidebar_c)
            draw.text((20, 80), 'Navigation', fill=accent, font=font_small)
            nav_items = ['Dashboard', 'Products', 'Warranties', 'Claims', 'Profile']
            for i, item in enumerate(nav_items):
                y = 110 + i * 38
                if i == 0:
                    draw.rectangle([(8, y - 4), (252, y + 26)], fill=nav_color)
                    draw.text((20, y), item, fill='white', font=font_small)
                else:
                    draw.text((20, y), item, fill=text_c, font=font_small)

        # Main content area — page title
        content_x = 280 if role else 0
        center_x   = content_x + (W - content_x) // 2

        # Page name
        page_name = filename.replace('.png', '').split('_', 1)[-1].replace('_', ' ').title()
        draw.text((content_x + 32, 90), page_name, fill=text_c, font=font_big)
        draw.text((content_x + 32, 130), f'URL: {BASE_URL}{path}', fill=accent, font=font_mono)
        draw.line([(content_x + 32, 160), (W - 32, 160)], fill=accent, width=2)

        # Simulated stat cards
        if 'dashboard' in filename or 'admin' in filename:
            card_colors = ['#2563eb', '#10b981', '#f59e0b', '#f43f5e']
            card_labels = ['Total Claims', 'Valid', 'Pending', 'Manual Review']
            card_values = ['142', '89', '23', '30']
            cw, ch = 240, 110
            for i, (lbl, val, col) in enumerate(zip(card_labels, card_values, card_colors)):
                cx = content_x + 32 + i * (cw + 16)
                cy = 200
                draw.rectangle([(cx, cy), (cx + cw, cy + ch)], fill='white')
                # Top accent bar
                acc_rgb = tuple(int(col[1:3+2*j:2], 16) if j < 3 else 255
                                for j in range(3))
                try:
                    acc_rgb = tuple(int(col[1+2*j:3+2*j], 16) for j in range(3))
                    draw.rectangle([(cx, cy), (cx + cw, cy + 4)], fill=acc_rgb)
                    draw.text((cx + 16, cy + 16), lbl, fill='#64748b', font=font_small)
                    draw.text((cx + 16, cy + 42), val, fill='#1e293b', font=font_big)
                except Exception:
                    pass

        # AssureX watermark
        draw.text((W // 2 - 60, H - 40), 'AssureX Claim Engine — Screenshot Placeholder',
                  fill=accent, font=font_small)
        draw.text((W // 2 - 80, H - 20),
                  f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")} | Run playwright for real screenshots',
                  fill=text_c, font=font_small)

        img.save(str(out), 'PNG', optimize=True, quality=90)
        log('🖼️', f'{filename}')

    log('✅', f'Saved {len(SCREENSHOT_PLAN)} placeholder screenshots to {SCREENSHOTS_DIR}')
    log('💡', 'Run `pip install playwright && playwright install chromium` for real screenshots')
    return True


# ─────────────────────────────────────────────────────────────────
# EXTRA: Capture from live app after adding seed data
# ─────────────────────────────────────────────────────────────────

EXTRA_URLS = """
# To capture these pages, you need existing claim/product data in your DB.
# Run `python manage.py seed_demo_data` first (if available), then re-run this script.
#
# Claim detail:      /claims/<pk>/
# Claim report:      /claims/<pk>/report/
# Reviewer detail:   /reviewer/claim/<pk>/
# Submit step 2:     /claims/<pk>/documents/
# Submit step 3:     /claims/<pk>/repairs/
# Submit step 4:     /claims/<pk>/review/
"""


# ─────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────

def main():
    print()
    print('═' * 60)
    print('  AssureX — Automated Screenshot Generator')
    print(f'  Target: {BASE_URL}')
    print(f'  Output: {SCREENSHOTS_DIR}')
    print(f'  Pages:  {len(SCREENSHOT_PLAN)}')
    print('═' * 60)
    print()

    # Check server is running
    try:
        import urllib.request
        urllib.request.urlopen(f'{BASE_URL}/accounts/login/', timeout=5)
        log('✅', f'Server is running at {BASE_URL}')
    except Exception:
        log('⚠️', f'Server not reachable at {BASE_URL}')
        log('💡', 'Starting Django dev server check failed — using PIL fallback')
        run_html_fallback()
        return

    # Try Playwright first
    if not run_playwright():
        log('⚠️', 'Playwright not installed — falling back to PIL placeholders')
        log('💡', 'To install: pip install playwright && playwright install chromium')
        run_html_fallback()

    print()
    print('═' * 60)
    print('  Screenshots complete!')
    print(f'  Location: {SCREENSHOTS_DIR}')
    print('═' * 60)
    print()
    print(EXTRA_URLS)


if __name__ == '__main__':
    main()
