"""AssureX — Seed realistic notifications for all users"""
from datetime import timedelta
from django.utils import timezone
from apps.accounts.models import User
from apps.notifications.models import Notification
from apps.claims.models import Claim

NOW = timezone.now()

customer  = User.objects.get(email='customer@assurex.com')
employee  = User.objects.get(email='employee@assurex.com')
reviewer  = User.objects.get(email='reviewer@assurex.com')
admin     = User.objects.get(email='admin@assurex.com')

# get claim refs
try:
    cl_approved = Claim.objects.filter(claimant=customer, status='approved').first()
    cl_manual   = Claim.objects.filter(status='manual').first()
    cl_rejected = Claim.objects.filter(claimant=customer, status='rejected').first()
    cl_eval     = Claim.objects.filter(status='evaluation').first()
except: pass

def n(recipient, ntype, priority, title, message, link='', obj_type='', obj_id='', days_ago=0, read=False):
    exists = Notification.objects.filter(recipient=recipient, title=title).exists()
    if exists:
        print(f'  skip: {title[:45]}')
        return
    notif = Notification.objects.create(
        recipient=recipient, notification_type=ntype, priority=priority,
        title=title, message=message, link=link,
        object_type=obj_type, object_id=str(obj_id) if obj_id else '',
        is_read=read,
    )
    # backdate
    if days_ago:
        from django.db import connection
        connection.cursor().execute(
            "UPDATE notifications SET created_at = %s WHERE id = %s",
            [NOW - timedelta(days=days_ago), notif.pk]
        )
    print(f'  + [{priority.upper()}] {title[:50]}')

print('\n── Customer: Ahmed Khan ─────────────────')
n(customer, 'claim_approved',  'high',
  f'Claim {cl_approved.claim_reference} Approved ✓' if cl_approved else 'Claim Approved',
  'Your warranty claim for Samsung Galaxy S24 Ultra has been approved. The display flickering issue is covered under your manufacturer warranty. Please proceed to the nearest service center.',
  f'/claims/{cl_approved.pk}/' if cl_approved else '', 'Claim', cl_approved.pk if cl_approved else '',
  days_ago=9, read=True)

n(customer, 'claim_submitted', 'medium',
  'Claim CLM-0000002 Successfully Submitted',
  'Your claim for Samsung Galaxy S24 Ultra has been submitted and is now under AI evaluation. You will be notified once the decision is ready.',
  f'/claims/{cl_approved.pk}/' if cl_approved else '',
  days_ago=9, read=True)

n(customer, 'claim_rejected',  'high',
  f'Claim {cl_rejected.claim_reference} Rejected' if cl_rejected else 'Claim Rejected',
  'Your claim for LG OLED C3 65-inch TV has been rejected. Reason: The warranty expired 35 days before the reported fault date. The claim falls outside the warranty coverage period.',
  f'/claims/{cl_rejected.pk}/' if cl_rejected else '', 'Claim', cl_rejected.pk if cl_rejected else '',
  days_ago=4, read=True)

n(customer, 'warranty_expiry', 'high',
  'Warranty Expiring in 18 Days — Samsung Galaxy S24 Ultra',
  'Your Samsung Galaxy S24 Ultra warranty is expiring on Oct 15, 2027. Consider purchasing an extended warranty or submitting any pending claims before expiry.',
  '/warranties/', days_ago=2, read=False)

n(customer, 'claim_status',    'medium',
  'Claim CLM-0000003 Sent to Manual Review',
  'Your Lenovo ThinkPad X1 Carbon claim has been escalated to manual review. Our AI models returned mixed confidence results. A reviewer will assess your case within 2 business days.',
  f'/claims/{cl_manual.pk}/' if cl_manual else '', days_ago=19, read=True)

n(customer, 'system',          'low',
  'Welcome to AssureX — Your Claims Dashboard is Ready',
  'Your AssureX account is set up. You can now register products, submit warranty claims, and track their status in real time using our AI-powered engine.',
  '/dashboard/customer/', days_ago=180, read=True)

print('\n── Employee: Sara Ali ───────────────────')
n(employee, 'claim_approved',  'medium',
  'Claim CLM-0000006 Approved — OPPO Reno 11 Pro',
  'The claim you submitted on behalf of Ali Raza for OPPO Reno 11 Pro has been approved. Front camera manufacturing defect confirmed by AI evaluation.',
  '/claims/', days_ago=7, read=True)

n(employee, 'claim_approved',  'medium',
  'Claim CLM-0000007 Approved — HP EliteBook 840 G11',
  'The claim submitted for Fatima Noor (HP EliteBook 840 G11 keyboard fault) has been approved. Proceeding to repair authorization.',
  '/claims/', days_ago=13, read=True)

n(employee, 'claim_status',    'high',
  'Claim CLM-0000008 Escalated to Manual Review',
  'Haier washing machine claim for Usman Tariq has mixed AI confidence results. The claim has been escalated for manual review. Monitor the queue for updates.',
  '/claims/', days_ago=4, read=False)

n(employee, 'missing_docs',    'high',
  'Missing Documents — CLM-0000010 Requires Attention',
  'HP EliteBook display claim (CLM-0000010) is missing fault evidence photo and purchase receipt. Please contact Fatima Noor to upload the required documents before submission.',
  '/claims/', days_ago=1, read=False)

n(employee, 'duplicate_alert', 'critical',
  'Duplicate Document Detected — CLM-0000009',
  'A document uploaded for the PEL refrigerator claim (CLM-0000009) matches a file hash from a previously submitted claim. The claim has been flagged for review.',
  '/claims/', days_ago=1, read=False)

n(employee, 'system',          'low',
  'New Warranty Policy Updated — Smartphone Category',
  'The Smartphone Warranty Policy has been updated by the administrator. Claim reporting period changed from 14 to 21 days. Please inform customers accordingly.',
  '/warranties/', days_ago=5, read=True)

print('\n── Reviewer: Bilal Hassan ───────────────')
n(reviewer, 'claim_status',    'critical',
  '4 Claims Pending Manual Review in Queue',
  'There are currently 4 claims awaiting manual review in the queue. Oldest claim is 19 days old. Please prioritize CLM-0000003 (Lenovo ThinkPad) and CLM-0000008 (Haier Washer).',
  '/reviewer/queue/', days_ago=0, read=False)

n(reviewer, 'anomaly',         'critical',
  'AI Model Disagreement Detected — CLM-0000013',
  'Python ML and Vision models returned contradictory predictions on claim CLM-0000013 (PEL Fridge). Confidence difference: 19.2%. Manual review is mandatory.',
  '/reviewer/queue/', days_ago=1, read=False)

n(reviewer, 'claim_status',    'high',
  'Claim CLM-0000003 Assigned for Review',
  'Lenovo ThinkPad X1 Carbon battery claim has been assigned to you for manual review. AI confidence: Python 38% valid vs Vision 39% manual review. Decision required.',
  '/reviewer/queue/', days_ago=19, read=True)

n(reviewer, 'claim_status',    'medium',
  'Review Complete — CLM-0000002 Approved',
  'Your review decision for Samsung Galaxy S24 Ultra claim has been recorded. Status updated to Approved.',
  '/claims/', days_ago=9, read=True)

n(reviewer, 'system',          'low',
  'AI Threshold Updated by Administrator',
  'The minimum confidence threshold for auto-approval has been updated from 70% to 75%. Claims below this threshold will now be routed to manual review.',
  '/administrator/thresholds/', days_ago=3, read=True)

print('\n── Admin: System Admin ──────────────────')
n(admin, 'anomaly',            'critical',
  'System Alert: 1 Uncertain AI Result Detected Today',
  'Claim CLM-0000013 returned uncertain_result consistency status. Both models showed near-equal confidence across all 3 classes. Immediate manual review recommended.',
  '/administrator/monitoring/', days_ago=0, read=False)

n(admin, 'duplicate_alert',    'high',
  'Duplicate Claim Hash Flagged — CLM-0000009',
  'SHA-256 hash match detected: a document in CLM-0000009 was previously submitted in another claim. The claim has been flagged as potential duplicate.',
  '/administrator/all-claims/', days_ago=1, read=False)

n(admin, 'claim_status',       'medium',
  '15 Total Claims in System — 4 Pending Review',
  'System summary: 15 claims total, 5 approved, 2 rejected, 4 in manual review, 3 pending evaluation. Review queue requires attention.',
  '/administrator/', days_ago=0, read=False)

n(admin, 'system',             'medium',
  'Model Version Active: Random Forest v1.0 (98.22%)',
  'Python ML model (Random Forest) and Vision model (Gradient Boosting, 99.11%) are active and processing claims. No degradation detected in last 24 hours.',
  '/administrator/model-versions/', days_ago=2, read=True)

n(admin, 'warranty_expiry',    'medium',
  'LG OLED C3 Warranty Expired — Claim Filed Post-Expiry',
  'Customer Ahmed Khan filed a claim for LG OLED C3 65-inch after warranty expiry. The claim has been automatically rejected by the rule engine.',
  '/administrator/all-claims/', days_ago=4, read=True)

n(admin, 'system',             'low',
  'New User Registration: 3 Demo Customers Added',
  'Ali Raza, Fatima Noor, and Usman Tariq have been registered in the system as demo customers. 4 products and 5 employee-submitted claims created.',
  '/administrator/users/', days_ago=0, read=True)

print(f'\nTotal notifications: {Notification.objects.count()}')
for u in [customer, employee, reviewer, admin]:
    total = Notification.objects.filter(recipient=u).count()
    unread = Notification.objects.filter(recipient=u, is_read=False).count()
    print(f'  {u.first_name:<10} total={total}  unread={unread}')
