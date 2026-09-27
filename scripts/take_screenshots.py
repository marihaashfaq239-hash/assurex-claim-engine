"""
AssureX — Automated Screenshot Taker
Run after: pip install playwright && python -m playwright install chromium

Usage: python scripts/take_screenshots.py
"""
import asyncio
import os
from pathlib import Path

BASE_URL   = "http://127.0.0.1:8000"
SS_DIR     = Path(__file__).parent.parent / "screenshots"
VIEWPORT   = {"width": 1440, "height": 900}

# Login credentials
ADMIN_EMAIL    = "admin@assurex.com"
ADMIN_PASS     = "Admin@123"
CUSTOMER_EMAIL = "customer@assurex.com"
CUSTOMER_PASS  = "Customer@123"
EMPLOYEE_EMAIL = "employee@assurex.com"
EMPLOYEE_PASS  = "Employee@123"
REVIEWER_EMAIL = "reviewer@assurex.com"
REVIEWER_PASS  = "Reviewer@123"


async def login(page, email, password):
    await page.goto(f"{BASE_URL}/accounts/login/")
    await page.wait_for_load_state("networkidle")
    await page.fill('input[name="email"]', email)
    await page.fill('input[name="password"]', password)
    await page.click('button[type="submit"]')
    await page.wait_for_load_state("networkidle")


async def ss(page, filename, full_page=True):
    """Take screenshot and save."""
    await page.wait_for_timeout(800)  # let animations settle
    path = SS_DIR / filename
    await page.screenshot(path=str(path), full_page=full_page)
    print(f"  ✅  {filename}")


async def main():
    from playwright.async_api import async_playwright

    SS_DIR.mkdir(exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(viewport=VIEWPORT)
        page = await ctx.new_page()

        print("\n── Landing Page ─────────────────────────")
        await page.goto(f"{BASE_URL}/")
        await page.wait_for_timeout(2000)  # let Three.js load
        await ss(page, "00_landing.png", full_page=False)

        print("\n── Auth Pages ───────────────────────────")
        await page.goto(f"{BASE_URL}/accounts/login/")
        await page.wait_for_load_state("networkidle")
        await ss(page, "01_login.png")

        await page.goto(f"{BASE_URL}/accounts/register/")
        await page.wait_for_load_state("networkidle")
        await ss(page, "02_register.png")

        print("\n── Customer Pages ───────────────────────")
        await login(page, CUSTOMER_EMAIL, CUSTOMER_PASS)
        await ss(page, "03_customer_dashboard.png")

        await page.goto(f"{BASE_URL}/products/")
        await page.wait_for_load_state("networkidle")
        await ss(page, "04_products_list.png")

        await page.goto(f"{BASE_URL}/products/register/")
        await page.wait_for_load_state("networkidle")
        await ss(page, "05_product_register.png")

        await page.goto(f"{BASE_URL}/warranties/")
        await page.wait_for_load_state("networkidle")
        await ss(page, "06_warranties_list.png")

        await page.goto(f"{BASE_URL}/claims/submit/")
        await page.wait_for_load_state("networkidle")
        await ss(page, "07_claim_submit_step1.png")

        await page.goto(f"{BASE_URL}/claims/my-claims/")
        await page.wait_for_load_state("networkidle")
        await ss(page, "08_my_claims.png")

        await page.goto(f"{BASE_URL}/notifications/")
        await page.wait_for_load_state("networkidle")
        await ss(page, "09_notifications.png")

        await page.goto(f"{BASE_URL}/accounts/profile/")
        await page.wait_for_load_state("networkidle")
        await ss(page, "10_profile.png")

        print("\n── Admin Pages ──────────────────────────")
        await login(page, ADMIN_EMAIL, ADMIN_PASS)
        await ss(page, "11_admin_dashboard.png")

        await page.goto(f"{BASE_URL}/administrator/users/")
        await page.wait_for_load_state("networkidle")
        await ss(page, "12_admin_users.png")

        await page.goto(f"{BASE_URL}/administrator/all-claims/")
        await page.wait_for_load_state("networkidle")
        await ss(page, "13_admin_all_claims.png")

        await page.goto(f"{BASE_URL}/administrator/analytics/")
        await page.wait_for_load_state("networkidle")
        await ss(page, "14_admin_analytics.png")

        await page.goto(f"{BASE_URL}/administrator/model-versions/")
        await page.wait_for_load_state("networkidle")
        await ss(page, "15_admin_model_versions.png")

        await page.goto(f"{BASE_URL}/administrator/thresholds/")
        await page.wait_for_load_state("networkidle")
        await ss(page, "16_admin_thresholds.png")

        await page.goto(f"{BASE_URL}/administrator/warranty-policies/")
        await page.wait_for_load_state("networkidle")
        await ss(page, "17_admin_warranty_policies.png")

        await page.goto(f"{BASE_URL}/administrator/reports/")
        await page.wait_for_load_state("networkidle")
        await ss(page, "18_admin_export.png")

        await page.goto(f"{BASE_URL}/administrator/audit-logs/")
        await page.wait_for_load_state("networkidle")
        await ss(page, "19_admin_audit_logs.png")

        await page.goto(f"{BASE_URL}/administrator/monitoring/")
        await page.wait_for_load_state("networkidle")
        await ss(page, "20_admin_monitoring.png")

        print("\n── Reviewer Pages ───────────────────────")
        await login(page, REVIEWER_EMAIL, REVIEWER_PASS)
        await ss(page, "21_reviewer_dashboard.png")

        await page.goto(f"{BASE_URL}/reviewer/queue/")
        await page.wait_for_load_state("networkidle")
        await ss(page, "22_reviewer_queue.png")

        await page.goto(f"{BASE_URL}/reviewer/reviewed/")
        await page.wait_for_load_state("networkidle")
        await ss(page, "23_reviewer_reviewed.png")

        await browser.close()

        print(f"\n══════════════════════════════════════")
        print(f"Screenshots saved to: {SS_DIR}")
        total = len(list(SS_DIR.glob("*.png")))
        print(f"Total: {total} screenshots")
        print(f"══════════════════════════════════════\n")


if __name__ == "__main__":
    asyncio.run(main())
