"""
AssureX — Auto Screenshot Script using Edge headless + CDP
"""
import subprocess, time, os, json, base64, urllib.request
from pathlib import Path

BASE    = "http://127.0.0.1:8000"
SS_DIR  = Path(__file__).parent.parent / "screenshots"
EDGE    = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
DEBUG_PORT = 9222
W, H    = 1440, 900

# Credentials
CREDS = {
    'admin':    ('admin@assurex.com',    'Admin@123'),
    'customer': ('customer@assurex.com', 'Customer@123'),
    'employee': ('employee@assurex.com', 'Employee@123'),
    'reviewer': ('reviewer@assurex.com', 'Reviewer@123'),
}

def start_edge():
    proc = subprocess.Popen([
        EDGE,
        f'--remote-debugging-port={DEBUG_PORT}',
        '--headless=new',
        f'--window-size={W},{H}',
        '--no-first-run',
        '--no-default-browser-check',
        '--disable-extensions',
        '--disable-popup-blocking',
        '--user-data-dir=C:\\Temp\\edge_ss_profile',
        'about:blank'
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)
    return proc

def cdp(method, params=None):
    # Get websocket URL
    tabs = json.loads(urllib.request.urlopen(f'http://localhost:{DEBUG_PORT}/json').read())
    tab  = tabs[0]
    ws_id = tab['id']

    import websocket
    ws = websocket.create_connection(tab['webSocketDebuggerUrl'])
    msg = json.dumps({'id': 1, 'method': method, 'params': params or {}})
    ws.send(msg)
    resp = json.loads(ws.recv())
    ws.close()
    return resp

def navigate_and_screenshot(ws_url, url, filename, wait=1.5):
    import websocket
    ws = websocket.create_connection(ws_url)
    _id = [0]

    def send(method, params=None):
        _id[0] += 1
        ws.send(json.dumps({'id': _id[0], 'method': method, 'params': params or {}}))
        return json.loads(ws.recv())

    send('Page.navigate', {'url': url})
    time.sleep(wait)
    send('Emulation.setDeviceMetricsOverride', {'width': W, 'height': H, 'deviceScaleFactor': 1, 'mobile': False})
    resp = send('Page.captureScreenshot', {'format': 'png', 'captureBeyondViewport': False, 'clip': {'x':0,'y':0,'width':W,'height':H,'scale':1}})
    ws.close()

    if 'result' in resp and 'data' in resp['result']:
        img_data = base64.b64decode(resp['result']['data'])
        path = SS_DIR / filename
        with open(path, 'wb') as f:
            f.write(img_data)
        print(f"  ✅  {filename}")
        return True
    else:
        print(f"  ❌  {filename} — {resp}")
        return False


def main():
    # Check websocket-client
    try:
        import websocket
    except ImportError:
        print("Installing websocket-client...")
        subprocess.run(['pip', 'install', 'websocket-client', '-q'], check=True)
        import websocket

    SS_DIR.mkdir(exist_ok=True)
    print(f'\nStarting Edge headless...')
    proc = start_edge()

    try:
        # Get tab websocket URL
        for attempt in range(5):
            try:
                tabs = json.loads(urllib.request.urlopen(f'http://localhost:{DEBUG_PORT}/json').read())
                ws_url = tabs[0]['webSocketDebuggerUrl']
                break
            except:
                time.sleep(1)

        print(f'Edge ready. Taking screenshots...\n')

        def ss(url, filename, wait=1.8):
            navigate_and_screenshot(ws_url, url, filename, wait)

        # ── Landing ──
        print('── Landing ─────────────────────')
        ss(f'{BASE}/', '00_landing.png', wait=3)

        # ── Auth ──
        print('── Auth ────────────────────────')
        ss(f'{BASE}/accounts/login/',    '01_login.png')
        ss(f'{BASE}/accounts/register/', '02_register.png')

        # ── Login as customer ──
        print('── Customer ────────────────────')
        # Use Django login via POST
        import http.cookiejar, urllib.parse
        cj = http.cookiejar.CookieJar()

        def django_login(email, password):
            opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
            # get csrf
            resp = opener.open(f'{BASE}/accounts/login/')
            html = resp.read().decode()
            import re
            csrf = re.search(r'csrfmiddlewaretoken.*?value="([^"]+)"', html)
            csrf_token = csrf.group(1) if csrf else ''
            # post login
            data = urllib.parse.urlencode({'email': email, 'password': password, 'csrfmiddlewaretoken': csrf_token}).encode()
            req = urllib.request.Request(f'{BASE}/accounts/login/', data, headers={'Referer': f'{BASE}/accounts/login/', 'Content-Type': 'application/x-www-form-urlencoded'})
            opener.open(req)
            # Set cookies in Edge via CDP
            import websocket
            ws = websocket.create_connection(ws_url)
            _id = [0]
            for cookie in cj:
                _id[0] += 1
                ws.send(json.dumps({'id': _id[0], 'method': 'Network.setCookie', 'params': {'name': cookie.name, 'value': cookie.value, 'domain': 'localhost', 'path': '/'}}))
                ws.recv()
            ws.close()

        django_login(*CREDS['customer'])
        ss(f'{BASE}/dashboard/customer/', '03_customer_dashboard.png')
        ss(f'{BASE}/products/',           '04_products_list.png')
        ss(f'{BASE}/products/register/',  '05_product_register.png')
        ss(f'{BASE}/warranties/',         '06_warranties_list.png')
        ss(f'{BASE}/claims/submit/',      '07_claim_submit_step1.png')
        ss(f'{BASE}/claims/my-claims/',   '08_my_claims.png')
        ss(f'{BASE}/notifications/',      '09_notifications.png')
        ss(f'{BASE}/accounts/profile/',   '10_profile.png')

        print('── Admin ───────────────────────')
        django_login(*CREDS['admin'])
        ss(f'{BASE}/dashboard/admin/',                  '11_admin_dashboard.png')
        ss(f'{BASE}/administrator/users/',              '12_admin_users.png')
        ss(f'{BASE}/administrator/all-claims/',         '13_admin_all_claims.png')
        ss(f'{BASE}/administrator/analytics/',          '14_admin_analytics.png')
        ss(f'{BASE}/administrator/model-versions/',     '15_admin_model_versions.png')
        ss(f'{BASE}/administrator/thresholds/',         '16_admin_thresholds.png')
        ss(f'{BASE}/administrator/warranty-policies/',  '17_admin_warranty_policies.png')
        ss(f'{BASE}/administrator/reports/',            '18_admin_export.png')
        ss(f'{BASE}/administrator/audit-logs/',         '19_admin_audit_logs.png')
        ss(f'{BASE}/administrator/monitoring/',         '20_admin_monitoring.png')

        print('── Reviewer ────────────────────')
        django_login(*CREDS['reviewer'])
        ss(f'{BASE}/dashboard/reviewer/', '21_reviewer_dashboard.png')
        ss(f'{BASE}/reviewer/queue/',     '22_reviewer_queue.png')
        ss(f'{BASE}/reviewer/reviewed/',  '23_reviewer_reviewed.png')

    finally:
        proc.terminate()

    total = len(list(SS_DIR.glob('*.png')))
    print(f'\n✅ Done! {total} screenshots in screenshots/')

if __name__ == '__main__':
    main()
