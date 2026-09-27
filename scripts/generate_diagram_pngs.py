"""
AssureX — Generate Diagram PNGs using Matplotlib
Produces professional PNG diagrams for documentation
"""
import os, sys
sys.path.insert(0, '.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assurex.settings.development')

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.patheffects as pe
from pathlib import Path

OUT = Path(__file__).parent.parent / 'documentation' / 'diagrams'
OUT.mkdir(exist_ok=True)

BG   = '#003631'
TEAL = '#004a42'
BUTT = '#ffeda8'
ORG  = '#f57f17'
RED  = '#c62828'
GRN  = '#2e7d32'
BLU  = '#1565c0'
PUR  = '#880e4f'
WHT  = '#ffffff'

def save(fig, name):
    path = OUT / name
    fig.savefig(path, dpi=150, bbox_inches='tight',
                facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close(fig)
    print(f'  ✅  {name}')

# ═══════════════════════════════════════════════
# 1. SYSTEM ARCHITECTURE
# ═══════════════════════════════════════════════
def diagram_system_architecture():
    fig, ax = plt.subplots(figsize=(18, 12))
    fig.patch.set_facecolor('#f8f9fa')
    ax.set_facecolor('#f8f9fa')
    ax.set_xlim(0, 18); ax.set_ylim(0, 12)
    ax.axis('off')

    ax.text(9, 11.5, 'AssureX Claim Engine — System Architecture',
            ha='center', va='center', fontsize=16, fontweight='bold', color=BG)

    layers = [
        (0.3, 8.5, 17.4, 2.5, '#e8f5e9', '#003631', '👥  USER LAYER'),
        (0.3, 5.5, 17.4, 2.5, '#e3f2fd', '#1565c0', '🌐  WEB LAYER  —  Django 4.2 (Python 3.11)'),
        (0.3, 2.5, 17.4, 2.5, '#fff8e1', '#f57f17', '🤖  AI PIPELINE  —  src/ (Framework-Independent Python)'),
        (0.3, 0.1, 17.4, 2.0, '#fce4ec', '#880e4f', '🗄️  DATA LAYER'),
    ]
    for x, y, w, h, fc, ec, label in layers:
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.1',
                     facecolor=fc, edgecolor=ec, linewidth=2, zorder=1))
        ax.text(x+0.2, y+h-0.25, label, fontsize=11, fontweight='bold',
                color=ec, zorder=2)

    # User boxes
    users = [
        (1.0, 'Customer', '#003631'),
        (4.0, 'Employee', '#004a42'),
        (7.0, 'Reviewer', '#283593'),
        (10.0, 'Administrator', '#880e4f'),
        (13.5, 'Web Browser', '#455a64'),
    ]
    for x, label, color in users:
        ax.add_patch(FancyBboxPatch((x, 9.0), 2.2, 1.0, boxstyle='round,pad=0.1',
                     facecolor=color, edgecolor=BUTT, linewidth=1.5, zorder=3))
        ax.text(x+1.1, 9.5, label, ha='center', va='center',
                color=BUTT, fontsize=10, fontweight='bold', zorder=4)

    # Web app boxes
    apps = ['accounts', 'products', 'warranties', 'claims\n★', 'reviewer', 'administrator', 'notifications']
    colors_web = [BLU]*3 + ['#0d47a1'] + [BLU]*3
    for i, (app, col) in enumerate(zip(apps, colors_web)):
        x = 0.5 + i*2.4
        lw = 2.5 if '★' in app else 1.5
        ax.add_patch(FancyBboxPatch((x, 5.9), 2.1, 1.7, boxstyle='round,pad=0.1',
                     facecolor=col, edgecolor=BUTT, linewidth=lw, zorder=3))
        ax.text(x+1.05, 6.75, app.replace('\n★',''), ha='center', va='center',
                color=BUTT, fontsize=9, fontweight='bold', zorder=4)

    # AI boxes
    ai_modules = [
        ('📄 OCR\nTesseract+EasyOCR', ORG),
        ('⚙️ Preprocessing\n19 Features', ORG),
        ('🧠 Python ML\nRandom Forest\n98.22%', '#e65100'),
        ('🃏 Card\nGenerator', ORG),
        ('👁️ GTM Model\nGrad. Boosting\n99.11%', '#e65100'),
        ('📋 Rule Engine\n11 JSON Rules', ORG),
        ('⚖️ Decision\nEngine', '#bf360c'),
    ]
    for i, (label, color) in enumerate(ai_modules):
        x = 0.5 + i*2.4
        ax.add_patch(FancyBboxPatch((x, 2.9), 2.1, 1.7, boxstyle='round,pad=0.1',
                     facecolor=color, edgecolor=BUTT, linewidth=1.5, zorder=3))
        ax.text(x+1.05, 3.75, label, ha='center', va='center',
                color=WHT, fontsize=8.5, fontweight='bold', zorder=4)

    # Data boxes
    data = ['SQLite (Dev)\n16 Tables', 'PostgreSQL (Prod)\nRailway', 'Model Files\n.pkl files', 'Media Files\nclaim_docs/cards', 'Policy Files\n11 JSON rules']
    for i, label in enumerate(data):
        x = 0.8 + i*3.3
        ax.add_patch(FancyBboxPatch((x, 0.3), 2.8, 1.4, boxstyle='round,pad=0.1',
                     facecolor=PUR, edgecolor=WHT, linewidth=1.5, zorder=3))
        ax.text(x+1.4, 1.0, label, ha='center', va='center',
                color=WHT, fontsize=9, fontweight='bold', zorder=4)

    # Arrows
    ax.annotate('', xy=(8.5, 7.6), xytext=(8.5, 9.0),
                arrowprops=dict(arrowstyle='->', color=BG, lw=2), zorder=5)
    ax.annotate('', xy=(8.5, 4.65), xytext=(8.5, 5.9),
                arrowprops=dict(arrowstyle='->', color=ORG, lw=2), zorder=5)
    ax.annotate('', xy=(8.5, 1.7), xytext=(8.5, 2.9),
                arrowprops=dict(arrowstyle='->', color=PUR, lw=2), zorder=5)

    ax.text(8.9, 8.3, 'HTTP Requests', fontsize=9, color=BG, zorder=6)
    ax.text(8.9, 5.3, '_trigger_ai_pipeline()', fontsize=9, color=ORG, style='italic', zorder=6)
    ax.text(8.9, 2.3, 'Read/Write', fontsize=9, color=PUR, zorder=6)

    save(fig, 'system_architecture.png')

# ═══════════════════════════════════════════════
# 2. ER DIAGRAM
# ═══════════════════════════════════════════════
def diagram_er():
    fig, ax = plt.subplots(figsize=(20, 14))
    fig.patch.set_facecolor('#1a1a2e')
    ax.set_facecolor('#1a1a2e')
    ax.set_xlim(0, 20); ax.set_ylim(0, 14)
    ax.axis('off')
    ax.text(10, 13.5, 'AssureX — Entity Relationship Diagram (16 Tables)',
            ha='center', va='center', fontsize=16, fontweight='bold', color=BUTT)

    def table_box(x, y, name, cols, color=BG, w=3.2, h=None):
        if h is None:
            h = 0.45 * (len(cols) + 1)
        ax.add_patch(FancyBboxPatch((x, y-h), w, h, boxstyle='round,pad=0.05',
                     facecolor=color, edgecolor=BUTT, linewidth=1.5, zorder=2))
        ax.text(x+w/2, y-0.25, name, ha='center', va='center',
                color=BUTT, fontsize=9, fontweight='bold', zorder=3)
        ax.plot([x, x+w], [y-0.4, y-0.4], color=BUTT, lw=0.8, zorder=3)
        for i, col in enumerate(cols):
            ax.text(x+0.15, y-0.65-i*0.4, col, color='#cccccc', fontsize=7.5, zorder=3)

    def arrow(x1, y1, x2, y2, label=''):
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle='->', color=BUTT, lw=1.2,
                                    connectionstyle='arc3,rad=0.0'), zorder=4)
        if label:
            mx, my = (x1+x2)/2, (y1+y2)/2
            ax.text(mx, my+0.1, label, ha='center', fontsize=7, color='#aaaaaa', zorder=5)

    # users
    table_box(0.3, 13.0, 'users', ['PK id', 'UQ user_id', 'UQ email', 'role', 'first_name', 'last_name', 'is_active'])
    # product_categories
    table_box(4.2, 13.0, 'product_categories', ['PK id', 'UQ name', 'icon', 'is_active'])
    # products
    table_box(8.0, 13.0, 'products', ['PK id', 'FK owner_id', 'FK category_id', 'product_name', 'brand', 'serial_number', 'purchase_date'])
    # warranties
    table_box(12.0, 13.0, 'warranties', ['PK id', 'FK product_id', 'FK policy_id', 'warranty_type', 'start_date', 'expiry_date', 'status'])
    # warranty_policies
    table_box(16.2, 13.0, 'warranty_policies', ['PK id', 'FK category_id', 'name', 'duration_months', 'covered_faults', 'exclusions'])

    # claims (central — golden)
    table_box(7.5, 8.5, 'claims ★', ['PK id', 'UQ claim_reference', 'FK claimant_id', 'FK product_id', 'FK warranty_id',
                                       'status', 'final_decision', 'python_prediction', 'tm_prediction',
                                       'confidence_difference', 'model_consistency_status', 'rules_passed'],
              color='#1a3a2a', w=4.0)

    # child tables
    table_box(0.3, 7.0, 'claim_documents', ['PK id', 'FK claim_id', 'doc_type', 'file_hash (SHA-256)'])
    table_box(4.2, 7.0, 'ocr_results', ['PK id', 'FK document_id (1:1)', 'FK claim_id', 'serial_number', 'purchase_date', 'confidence'])
    table_box(12.5, 7.0, 'repair_history', ['PK id', 'FK claim_id', 'repair_date', 'is_authorized', 'outcome'])
    table_box(16.2, 7.0, 'model_predictions', ['PK id', 'FK claim_id', 'model_type', 'predicted_class', 'confidence_valid'])

    table_box(0.3, 3.5, 'rule_results', ['PK id', 'FK claim_id', 'rule_name', 'rule_type', 'outcome'])
    table_box(4.2, 3.5, 'reviews', ['PK id', 'FK claim_id (1:1)', 'FK reviewer_id', 'decision', 'is_ai_override'])
    table_box(8.0, 3.5, 'notifications', ['PK id', 'FK recipient_id', 'notification_type', 'priority', 'is_read'])
    table_box(12.0, 3.5, 'audit_logs', ['PK id', 'FK user_id', 'action_type', 'description', 'ip_address'])
    table_box(16.2, 3.5, 'model_versions', ['PK id', 'model_type', 'version_name', 'accuracy', 'is_active'])

    table_box(4.2, 0.8, 'system_configuration', ['PK id', 'UQ key', 'value', 'value_type'], color='#2a1a3a')

    # Relationships
    arrow(3.5, 10.8, 8.0, 10.2, '1:N')         # users → products
    arrow(7.5, 10.8, 4.8, 10.2, '1:N')          # product_categories → products
    arrow(11.2, 10.7, 12.0, 10.3, '1:N')        # products → warranties
    arrow(12.0, 10.2, 9.5, 8.5, '1:N')          # warranties → claims
    arrow(3.5, 12.5, 7.5, 7.5, '1:N')           # users → claims
    arrow(9.5, 7.5, 3.5, 5.5, '1:N')            # claims → claim_docs
    arrow(9.5, 7.5, 7.0, 5.5, '1:N')            # claims → ocr
    arrow(9.5, 7.5, 13.5, 5.5, '1:N')           # claims → repair
    arrow(9.5, 7.5, 17.0, 5.5, '1:N')           # claims → predictions
    arrow(9.5, 7.5, 2.0, 2.5, '1:N')            # claims → rule_results
    arrow(9.5, 7.5, 5.5, 2.5, '1:1')            # claims → reviews
    arrow(3.5, 12.5, 9.5, 2.5, '1:N')           # users → notifications
    arrow(3.5, 12.5, 13.5, 2.5, '1:N')          # users → audit_logs
    arrow(19.4, 10.7, 14.8, 10.3, '1:N')        # policies → warranties
    arrow(7.5, 11.5, 19.4, 11.0, '1:N')         # categories → policies

    save(fig, 'er_diagram.png')

# ═══════════════════════════════════════════════
# 3. USE CASE DIAGRAM
# ═══════════════════════════════════════════════
def diagram_use_case():
    fig, ax = plt.subplots(figsize=(18, 14))
    fig.patch.set_facecolor('#f8f9fa')
    ax.set_facecolor('#f8f9fa')
    ax.set_xlim(0, 18); ax.set_ylim(0, 14)
    ax.axis('off')
    ax.text(9, 13.5, 'AssureX — Use Case Diagram', ha='center', va='center',
            fontsize=16, fontweight='bold', color=BG)

    # System boundary
    ax.add_patch(FancyBboxPatch((2.0, 0.5), 14.5, 12.5, boxstyle='round,pad=0.2',
                 facecolor='white', edgecolor=BG, linewidth=2.5, zorder=1))
    ax.text(9.25, 12.8, 'AssureX Claim Engine', ha='center', va='center',
            fontsize=12, fontweight='bold', color=BG, zorder=2)

    def actor(x, y, label, color):
        # Head
        ax.add_patch(plt.Circle((x, y+0.5), 0.25, color=color, zorder=3))
        # Body
        ax.plot([x, x], [y+0.25, y-0.3], color=color, lw=2, zorder=3)
        # Arms
        ax.plot([x-0.3, x+0.3], [y+0.0, y+0.0], color=color, lw=2, zorder=3)
        # Legs
        ax.plot([x, x-0.25], [y-0.3, y-0.7], color=color, lw=2, zorder=3)
        ax.plot([x, x+0.25], [y-0.3, y-0.7], color=color, lw=2, zorder=3)
        ax.text(x, y-0.95, label, ha='center', va='center', fontsize=9,
                fontweight='bold', color=color, zorder=3)

    actor(0.9, 9.5,  'Customer',      '#003631')
    actor(0.9, 5.5,  'Employee',      '#004a42')
    actor(17.1, 8.5, 'Reviewer',      '#283593')
    actor(17.1, 5.0, 'Administrator', '#880e4f')
    actor(0.9, 2.0,  'AI System',     '#e65100')

    def uc(x, y, label, color='#e8f5e9', ec='#003631', w=2.6, h=0.55):
        ax.add_patch(mpatches.Ellipse((x, y), w, h, facecolor=color,
                     edgecolor=ec, linewidth=1.5, zorder=3))
        ax.text(x, y, label, ha='center', va='center',
                fontsize=8, color='#1a1a1a', zorder=4)

    # Customer UCs (left side)
    uc(5.0, 12.0, 'Register Account')
    uc(8.0, 12.0, 'Login')
    uc(5.0, 11.0, 'Register Product')
    uc(8.0, 11.0, 'View Warranties')
    uc(5.5, 10.0, 'Submit Claim (4-Step)', '#c8e6c9', GRN, 3.0)
    uc(8.5, 10.0, 'Upload Documents')
    uc(8.5,  9.0, 'Verify OCR Data')
    uc(5.5,  9.0, 'Track Claim Status')
    uc(5.5,  8.0, 'View AI Decision')
    uc(8.5,  8.0, 'Receive Notifications')
    uc(11.0, 12.0,'Update Profile')

    # Employee UCs
    uc(5.5, 6.5, 'Search Customer', '#e0f7fa', '#004a42')
    uc(8.5, 6.5, 'Submit on Behalf', '#b2ebf2', '#004a42', 2.8)
    uc(5.5, 5.5, 'View My Claims', '#e0f7fa', '#004a42')

    # AI UCs
    uc(5.5, 4.5, 'Extract OCR Data', '#fff8e1', ORG)
    uc(8.5, 4.5, 'Run Python ML', '#ffe0b2', '#e65100', 2.4)
    uc(5.5, 3.5, 'Generate Card', '#fff8e1', ORG)
    uc(8.5, 3.5, 'Run GTM Model', '#ffe0b2', '#e65100', 2.4)
    uc(5.5, 2.5, 'Run Rule Engine', '#fff8e1', ORG, 2.8)
    uc(8.5, 2.5, 'Final Decision', '#ffccbc', RED, 2.4)
    uc(11.0, 4.0, 'Detect Duplicates\n(SHA-256)', '#fff8e1', ORG)
    uc(11.0, 2.5, 'Detect Contradictions', '#fff8e1', ORG, 3.0)

    # Reviewer UCs
    uc(13.5, 10.5, 'View Review Queue', '#e8eaf6', '#283593')
    uc(13.5,  9.5, 'Review Claim', '#e8eaf6', '#283593')
    uc(13.5,  8.5, 'Approve/Reject', '#c5cae9', '#283593', 2.6)
    uc(13.5,  7.5, 'Override AI', '#e8eaf6', '#283593')
    uc(13.5,  6.5, 'Request More Info', '#e8eaf6', '#283593')

    # Admin UCs
    uc(13.5, 5.5, 'Admin Dashboard', '#fce4ec', PUR)
    uc(13.5, 4.5, 'Manage Users', '#fce4ec', PUR)
    uc(13.5, 3.5, 'AI Thresholds', '#f8bbd0', PUR)
    uc(13.5, 2.5, 'Warranty Policies', '#fce4ec', PUR)
    uc(11.0, 1.2, 'Export Reports/CSV', '#fce4ec', PUR)

    # Connections
    def connect(x1, y1, x2, y2, color='#003631', dash=False):
        ls = '--' if dash else '-'
        ax.plot([x1, x2], [y1, y2], ls, color=color, lw=1.0, zorder=2, alpha=0.7)

    for uy in [12.0, 11.0, 10.0, 9.0, 8.0]:
        connect(1.4, 9.5, 3.7, uy)
    for uy in [6.5, 5.5]:
        connect(1.4, 5.5, 3.1, uy, '#004a42')
    for uy in [4.5, 3.5, 2.5]:
        connect(1.4, 2.0, 3.1, uy, '#e65100')
    for uy in [10.5, 9.5, 8.5, 7.5, 6.5]:
        connect(16.6, 8.5, 14.8, uy, '#283593')
    for uy in [5.5, 4.5, 3.5, 2.5]:
        connect(16.6, 5.0, 14.8, uy, PUR)

    # include
    connect(6.8, 10.0, 7.2, 10.0, '#666', True)
    connect(7.2, 10.0, 7.2, 4.5, '#666', True)
    ax.text(6.9, 7.2, '<<include>>', fontsize=7, color='#666', style='italic')

    save(fig, 'use_case.png')

# ═══════════════════════════════════════════════
# 4. DFD LEVEL 0
# ═══════════════════════════════════════════════
def diagram_dfd0():
    fig, ax = plt.subplots(figsize=(14, 10))
    fig.patch.set_facecolor('#fafafa')
    ax.set_facecolor('#fafafa')
    ax.set_xlim(0, 14); ax.set_ylim(0, 10)
    ax.axis('off')
    ax.text(7, 9.6, 'AssureX — DFD Level 0 (Context Diagram)',
            ha='center', va='center', fontsize=15, fontweight='bold', color=BG)

    def ext(x, y, label, color, w=2.2, h=0.9):
        ax.add_patch(FancyBboxPatch((x-w/2, y-h/2), w, h, boxstyle='round,pad=0.08',
                     facecolor=color, edgecolor=WHT, linewidth=1.5, zorder=3))
        ax.text(x, y, label, ha='center', va='center',
                color=WHT, fontsize=10, fontweight='bold', zorder=4)

    def flow(x1, y1, x2, y2, label, color=BG):
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle='->', color=color, lw=2.0,
                    connectionstyle='arc3,rad=0.0'), zorder=5)
        mx, my = (x1+x2)/2, (y1+y2)/2
        ax.text(mx, my+0.12, label, ha='center', fontsize=8,
                color='#444', zorder=6, bbox=dict(fc='white', ec='none', pad=1))

    # Central process
    ax.add_patch(plt.Circle((7, 5), 1.8, facecolor=BG, edgecolor=BUTT, linewidth=2.5, zorder=3))
    ax.text(7, 5.15, 'AssureX', ha='center', va='center',
            color=BUTT, fontsize=14, fontweight='bold', zorder=4)
    ax.text(7, 4.75, 'Claim Engine', ha='center', va='center',
            color=BUTT, fontsize=11, zorder=4)

    ext(2.0, 8.0, 'Customer',  '#003631')
    ext(2.0, 5.0, 'Employee',  '#004a42')
    ext(2.0, 2.0, 'AI System\n(ML+GTM+Rules)', '#e65100')
    ext(12.0, 8.0, 'Reviewer',       '#283593')
    ext(12.0, 5.0, 'Administrator',   '#880e4f')
    ext(7.0, 8.5, 'Model Files\n(pkl)', '#f57f17', 2.5, 0.8)
    ext(7.0, 1.5, 'Database\n(SQLite/PostgreSQL)', '#455a64', 3.0, 0.9)

    flow(3.1, 8.0, 5.2, 5.8, 'Claim details, documents')
    flow(5.4, 6.2, 3.1, 7.7, 'Decision, status, notifications', '#003631')
    flow(3.1, 5.0, 5.2, 5.1, 'On-behalf claim data')
    flow(5.4, 4.9, 3.1, 4.8, 'Claim results', '#004a42')
    flow(11.0, 8.0, 8.8, 5.7, 'Review decision, override', '#283593')
    flow(8.8, 6.2, 11.0, 7.7, 'Review queue, AI results', '#283593')
    flow(11.0, 5.0, 8.8, 5.1, 'Config, thresholds', '#880e4f')
    flow(8.8, 4.9, 11.0, 4.8, 'Analytics, reports', '#880e4f')
    flow(7.0, 6.8, 7.0, 8.1, 'Load model, run inference', ORG)
    flow(7.0, 3.2, 7.0, 2.0, 'Read/Write all records', '#455a64')
    flow(3.1, 2.3, 5.2, 4.5, 'Predictions, rule results', '#e65100')

    save(fig, 'dfd_level0.png')

# ═══════════════════════════════════════════════
# 5. ACTIVITY DIAGRAM
# ═══════════════════════════════════════════════
def diagram_activity():
    fig, ax = plt.subplots(figsize=(10, 18))
    fig.patch.set_facecolor('#fafafa')
    ax.set_facecolor('#fafafa')
    ax.set_xlim(0, 10); ax.set_ylim(0, 18)
    ax.axis('off')
    ax.text(5, 17.6, 'Activity Diagram — Claim Submission & AI Evaluation',
            ha='center', va='center', fontsize=14, fontweight='bold', color=BG)

    def box(x, y, label, color='#e8f5e9', ec='#003631', w=4.0, h=0.7):
        ax.add_patch(FancyBboxPatch((x-w/2, y-h/2), w, h, boxstyle='round,pad=0.08',
                     facecolor=color, edgecolor=ec, linewidth=1.5, zorder=3))
        ax.text(x, y, label, ha='center', va='center',
                fontsize=9, color='#1a1a1a', fontweight='bold', zorder=4)

    def diamond(x, y, label):
        d = plt.Polygon([[x, y+0.5], [x+1.2, y], [x, y-0.5], [x-1.2, y]],
                        closed=True, facecolor='#fff9c4', edgecolor=ORG, lw=1.5, zorder=3)
        ax.add_patch(d)
        ax.text(x, y, label, ha='center', va='center', fontsize=8, zorder=4)

    def arr(y1, y2, x=5.0, color=BG):
        ax.annotate('', xy=(x, y2), xytext=(x, y1),
                    arrowprops=dict(arrowstyle='->', color=color, lw=1.5), zorder=5)

    # Start
    ax.add_patch(plt.Circle((5, 17.1), 0.25, color=BG, zorder=4))
    arr(17.1, 16.6)

    box(5, 16.3, 'Customer Logs In')
    arr(15.95, 15.45)
    box(5, 15.1, 'Step 1: Enter Fault Details\n(product, fault date, damage type)', h=0.8)
    arr(14.7, 14.2)
    diamond(5, 13.9, 'Fields Valid?')

    # No branch
    ax.plot([6.2, 7.5, 7.5], [13.9, 13.9, 14.8], color=RED, lw=1.5, zorder=3)
    ax.add_patch(FancyBboxPatch((6.8, 14.5), 2.2, 0.6, boxstyle='round,pad=0.05',
                 facecolor='#ffcdd2', edgecolor=RED, lw=1.5, zorder=3))
    ax.text(7.9, 14.8, 'Show errors\nReturn to form', ha='center', va='center', fontsize=8, zorder=4)
    ax.text(6.6, 14.1, 'No', fontsize=8, color=RED)

    arr(13.4, 12.9, color=GRN)
    ax.text(5.2, 13.15, 'Yes', fontsize=8, color=GRN)

    box(5, 12.6, 'Step 2: Upload Documents')
    arr(12.25, 11.75)
    box(5, 11.45, 'System OCR Extraction\n(Tesseract + EasyOCR)', color='#fff8e1', ec=ORG, h=0.8)
    arr(11.05, 10.55)
    box(5, 10.25, 'Customer Verifies OCR Data')
    arr(9.9, 9.4)
    box(5, 9.1, 'Step 3: Repair History (optional)')
    arr(8.75, 8.25)
    box(5, 7.95, 'Step 4: Review + Contradiction Check')
    arr(7.6, 7.1)
    diamond(5, 6.8, 'Hard\nContradictions?')

    ax.plot([6.2, 7.5, 7.5], [6.8, 6.8, 7.5], color=RED, lw=1.5, zorder=3)
    ax.add_patch(FancyBboxPatch((6.8, 7.2), 2.2, 0.6, boxstyle='round,pad=0.05',
                 facecolor='#ffcdd2', edgecolor=RED, lw=1.5, zorder=3))
    ax.text(7.9, 7.5, 'Show contradiction\nFix required', ha='center', va='center', fontsize=8, zorder=4)
    ax.text(6.6, 7.0, 'No❌', fontsize=8, color=RED)

    arr(6.3, 5.85, color=GRN)
    ax.text(5.2, 6.05, 'Yes✓', fontsize=8, color=GRN)

    box(5, 5.55, 'Submit Claim → AI Pipeline Triggered', color='#c8e6c9', ec=GRN)
    arr(5.2, 4.7)

    # Fork
    ax.add_patch(plt.Rectangle((2.5, 4.5), 5.0, 0.2, color=BG, zorder=4))
    ax.plot([3.0, 3.0], [4.5, 4.1], color=ORG, lw=1.5, zorder=5)
    ax.plot([7.0, 7.0], [4.5, 4.1], color=ORG, lw=1.5, zorder=5)

    box(3.0, 3.75, 'Python ML\n(Random Forest)', color='#ffe0b2', ec='#e65100', w=3.2)
    box(7.0, 3.75, 'GTM Model\n(Gradient Boost)', color='#ffe0b2', ec='#e65100', w=3.2)

    # Join
    ax.plot([3.0, 3.0], [3.4, 3.0], color=ORG, lw=1.5, zorder=5)
    ax.plot([7.0, 7.0], [3.4, 3.0], color=ORG, lw=1.5, zorder=5)
    ax.add_patch(plt.Rectangle((2.5, 2.8), 5.0, 0.2, color=BG, zorder=4))

    arr(2.8, 2.3)
    box(5, 2.0, 'Compare + Run Rule Engine', color='#fff8e1', ec=ORG)
    arr(1.65, 1.15)

    # Final 3 outcomes
    for x, label, color, ec in [(2.0, '✅ Valid', '#c8e6c9', GRN),
                                  (5.0, '🔍 Manual', '#fff9c4', ORG),
                                  (8.0, '❌ Invalid', '#ffcdd2', RED)]:
        ax.add_patch(FancyBboxPatch((x-1.3, 0.5), 2.6, 0.6, boxstyle='round,pad=0.08',
                     facecolor=color, edgecolor=ec, lw=2, zorder=3))
        ax.text(x, 0.8, label, ha='center', va='center', fontsize=10, fontweight='bold', zorder=4)
        ax.plot([5, x], [1.15, 1.1], color='#666', lw=1.2, zorder=3)

    # End
    ax.add_patch(plt.Circle((5, 0.2), 0.15, color=BG, zorder=4))
    ax.add_patch(plt.Circle((5, 0.2), 0.22, facecolor='none', edgecolor=BG, lw=2, zorder=4))

    save(fig, 'activity_diagram.png')

# ═══════════════════════════════════════════════
# 6. SEQUENCE DIAGRAM
# ═══════════════════════════════════════════════
def diagram_sequence():
    fig, ax = plt.subplots(figsize=(20, 14))
    fig.patch.set_facecolor('#fafafa')
    ax.set_facecolor('#fafafa')
    ax.set_xlim(0, 20); ax.set_ylim(0, 14)
    ax.axis('off')
    ax.text(10, 13.6, 'Sequence Diagram — Claim Submission to Final Decision',
            ha='center', va='center', fontsize=15, fontweight='bold', color=BG)

    actors = [
        ('Customer', 1.0, '#003631'),
        ('Django\nViews', 3.2, BLU),
        ('OCR\nExtractor', 5.4, ORG),
        ('Preprocessor\n19 features', 7.6, ORG),
        ('Python ML\nRandom Forest', 10.0, '#e65100'),
        ('Card\nGenerator', 12.4, ORG),
        ('GTM Model\nGrad.Boost', 14.8, '#e65100'),
        ('Decision\nEngine', 17.2, '#bf360c'),
        ('Database', 19.5, PUR),
    ]

    # Headers
    for label, x, color in actors:
        ax.add_patch(FancyBboxPatch((x-0.9, 12.6), 1.8, 0.9, boxstyle='round,pad=0.05',
                     facecolor=color, edgecolor=WHT, lw=1.5, zorder=3))
        ax.text(x, 13.05, label, ha='center', va='center', color=WHT,
                fontsize=8, fontweight='bold', zorder=4)

    # Lifelines
    for _, x, color in actors:
        ax.plot([x, x], [12.6, 0.5], ':', color=color, lw=1.2, alpha=0.5, zorder=1)

    def msg(y, x1, x2, label, color=BG, ret=False):
        ls = '--' if ret else '-'
        style = '<-' if ret else '->'
        ax.annotate('', xy=(x2, y), xytext=(x1, y),
                    arrowprops=dict(arrowstyle=style, color=color,
                                    lw=1.8, linestyle=ls), zorder=5)
        mx = (x1 + x2) / 2
        ax.text(mx, y+0.12, label, ha='center', fontsize=7.5,
                color='#333', zorder=6, bbox=dict(fc='white', ec='none', pad=1))

    def note(y, label, color='#f5f5f5'):
        ax.add_patch(FancyBboxPatch((0.0, y-0.18), 19.9, 0.36, boxstyle='round,pad=0.02',
                     facecolor=color, edgecolor='#ccc', lw=0.5, zorder=2, alpha=0.4))
        ax.text(0.15, y, label, va='center', fontsize=7.5, color='#555', zorder=6)

    note(11.8, '① Claim Step 1 — Fault Details', '#e8f5e9')
    msg(11.5, 1.0, 3.2, 'POST /claims/submit/ (fault details)')
    msg(11.0, 3.2, 19.5, 'save Draft Claim', PUR)
    msg(10.6, 19.5, 3.2, 'claim.pk returned', PUR, True)

    note(10.0, '② Claim Step 2 — Upload Document + OCR', '#e8f5e9')
    msg(9.7, 1.0, 3.2, 'POST /claims/submit/step2 (document file)')
    msg(9.2, 3.2, 5.4, 'extract_document_data(file_path)', ORG)
    msg(8.7, 5.4, 3.2, 'extracted_fields + confidence', ORG, True)
    msg(8.3, 3.2, 19.5, 'save ClaimDocument + OCRResult + hash', PUR)

    note(7.6, '③ Claim Step 4 — Submit + Trigger AI Pipeline', '#fff8e1')
    msg(7.3, 1.0, 3.2, 'POST /submit/step4  →  SUBMIT CLAIM')
    msg(6.8, 3.2, 7.6, '_trigger_ai_pipeline(claim)', ORG)
    msg(6.3, 7.6, 10.0, 'extract_features() → 19 features')
    msg(5.8, 10.0, 10.0, 'predict(features_df)', '#e65100')
    msg(5.3, 10.0, 7.6, '{class, conf_v, conf_i, conf_m}', '#e65100', True)
    msg(4.8, 7.6, 12.4, 'generate_claim_card(claim)', ORG)
    msg(4.3, 12.4, 7.6, 'card_path.png returned', ORG, True)
    msg(3.8, 7.6, 14.8, 'predict_from_card(card_path)', '#e65100')
    msg(3.3, 14.8, 7.6, '{class, conf_v, conf_i, conf_m}', '#e65100', True)
    msg(2.8, 7.6, 17.2, 'evaluate(py, tm, features)', '#bf360c')
    msg(2.3, 17.2, 7.6, 'final_decision + consistency', '#bf360c', True)
    msg(1.8, 7.6, 19.5, 'save all results to claims table', PUR)
    msg(1.3, 3.2, 1.0, 'redirect → claim detail + notification', BG, True)

    save(fig, 'sequence_diagram.png')

# ═══════════════════════════════════════════════
# 7. DECISION FLOW
# ═══════════════════════════════════════════════
def diagram_decision():
    fig, ax = plt.subplots(figsize=(12, 16))
    fig.patch.set_facecolor('#fafafa')
    ax.set_facecolor('#fafafa')
    ax.set_xlim(0, 12); ax.set_ylim(0, 16)
    ax.axis('off')
    ax.text(6, 15.6, 'Decision Flow — AI Claim Evaluation Pipeline',
            ha='center', va='center', fontsize=14, fontweight='bold', color=BG)

    def box(x, y, label, color='#e8f5e9', ec=BG, w=3.5, h=0.7):
        ax.add_patch(FancyBboxPatch((x-w/2, y-h/2), w, h, boxstyle='round,pad=0.08',
                     facecolor=color, edgecolor=ec, lw=1.8, zorder=3))
        ax.text(x, y, label, ha='center', va='center', fontsize=9, zorder=4)

    def diamond(x, y, label):
        d = plt.Polygon([[x, y+0.65], [x+1.5, y], [x, y-0.65], [x-1.5, y]],
                        closed=True, facecolor='#fff9c4', edgecolor=ORG, lw=2, zorder=3)
        ax.add_patch(d)
        ax.text(x, y, label, ha='center', va='center', fontsize=8.5, zorder=4)

    def arr(x1, y1, x2, y2, label='', color=BG):
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle='->', color=color, lw=1.8), zorder=5)
        if label:
            mx, my = (x1+x2)/2, (y1+y2)/2
            ax.text(mx+0.1, my+0.1, label, fontsize=8, color=color, fontweight='bold', zorder=6)

    # Start
    ax.add_patch(plt.Circle((6, 15.1), 0.3, color=BG, zorder=4))
    arr(6, 14.8, 6, 14.3)

    box(6, 14.0, 'Claim Submitted', BG, BG, 3.5, 0.55)
    ax.texts[-1].set_color(BUTT)
    arr(6, 13.7, 6, 13.2)

    box(6, 12.9, 'Extract 19 Features\n(Preprocessing)', '#fff8e1', ORG)
    arr(6, 12.55, 6, 12.1)

    # Fork
    ax.add_patch(plt.Rectangle((2.5, 11.95), 7.0, 0.15, color=BG, zorder=4))
    arr(3.5, 11.95, 3.5, 11.45)
    arr(8.5, 11.95, 8.5, 11.45)
    ax.text(3.0, 12.2, 'Parallel', fontsize=8, color=BG)

    box(3.5, 11.0, 'Python ML Model\n(Random Forest)', '#ffe0b2', '#e65100')
    box(8.5, 11.0, 'Generate Card → GTM Model\n(Gradient Boosting)', '#ffe0b2', '#e65100')

    # Join
    arr(3.5, 10.65, 3.5, 10.2)
    arr(8.5, 10.65, 8.5, 10.2)
    ax.add_patch(plt.Rectangle((2.5, 10.05), 7.0, 0.15, color=BG, zorder=4))
    arr(6, 10.05, 6, 9.6)

    box(6, 9.3, 'Compare Predictions\nconf_diff = |py_top − tm_top|', '#e8eaf6', '#283593')
    arr(6, 8.95, 6, 8.45)

    diamond(6, 8.0, 'Both models\npredict same class?')
    arr(4.5, 8.0, 2.5, 8.0, 'NO', RED)
    arr(6, 7.35, 6, 6.9, 'YES', GRN)

    box(1.5, 8.0, 'MODEL\nDISAGREEMENT', '#ffcdd2', RED, 2.2)

    diamond(6, 6.5, 'conf_diff ≤ 5%?\n(Strong Match)')
    arr(4.5, 6.5, 3.0, 6.5, 'YES ✓', GRN)
    arr(6, 6.15, 6, 5.7, 'NO', '#666')

    box(2.0, 6.5, 'STRONG MATCH', '#c8e6c9', GRN, 2.0)

    diamond(6, 5.3, 'conf_diff ≤ 15%?\n(Acceptable)')
    arr(4.5, 5.3, 3.0, 5.3, 'YES ✓', GRN)
    arr(6, 4.95, 6, 4.5, 'NO → WEAK', ORG)
    box(2.0, 5.3, 'ACCEPTABLE MATCH', '#dcedc8', '#558b2f', 2.2)

    # All paths → Rule Engine
    ax.plot([2.0, 2.0, 6, 1.5, 1.5, 6], [6.15, 4.3, 4.3, 7.65, 4.3, 4.3],
            color='#999', lw=1, ls='--', zorder=2)
    box(6, 4.1, 'Run Rule Engine\n(11 Warranty Rules)', '#fff8e1', ORG)
    arr(6, 3.75, 6, 3.25)

    diamond(6, 2.85, 'Hard Fail\nRule Triggered?')
    arr(7.5, 2.85, 9.5, 2.85, 'YES', RED)
    arr(6, 2.2, 6, 1.75, 'NO', GRN)

    box(10.2, 2.85, '❌ LIKELY\nINVALID', '#c62828', '#c62828', 2.0)
    ax.texts[-1].set_color(WHT)

    diamond(6, 1.35, 'High Confidence\n+ Strong/Acceptable?')
    arr(4.5, 1.35, 2.8, 1.35, 'YES', GRN)
    arr(7.5, 1.35, 9.5, 1.35, 'NO', ORG)

    box(1.8, 1.35, '✅ LIKELY\nVALID', '#2e7d32', '#2e7d32', 2.0)
    ax.texts[-1].set_color(WHT)
    box(10.2, 1.35, '🔍 MANUAL\nREVIEW', ORG, ORG, 2.0)
    ax.texts[-1].set_color(WHT)

    save(fig, 'decision_flow.png')

# ═══════════════════════════════════════════════
# RUN ALL
# ═══════════════════════════════════════════════
print('\n══════════════════════════════════════════')
print('  AssureX — Generating Diagram PNGs')
print('══════════════════════════════════════════\n')

diagram_system_architecture()
diagram_er()
diagram_use_case()
diagram_dfd0()
diagram_activity()
diagram_sequence()
diagram_decision()

print(f'\n✅ All 7 diagrams saved to:')
print(f'   {OUT}\n')
