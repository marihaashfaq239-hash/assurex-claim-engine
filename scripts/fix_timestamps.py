"""Fix claim created_at timestamps so recent claims table shows all customers"""
from datetime import timedelta
from django.utils import timezone
from django.db import connection
from apps.claims.models import Claim

now = timezone.now()

# Assign staggered created_at so all 15 claims spread across last 7 days
# newest = today, oldest = 7 days ago
claims = list(Claim.objects.order_by('pk'))

# Give each claim a distinct timestamp spread over last 7 days
# CLM-0000006 to 0000015 = employee + admin extras = newer
timestamps = {
    1:  now - timedelta(days=7, hours=3),
    2:  now - timedelta(days=6, hours=5),
    3:  now - timedelta(days=6, hours=2),
    4:  now - timedelta(days=5, hours=4),
    5:  now - timedelta(days=5, hours=1),
    6:  now - timedelta(days=4, hours=6),
    7:  now - timedelta(days=4, hours=2),
    8:  now - timedelta(days=3, hours=5),
    9:  now - timedelta(days=3, hours=1),
    10: now - timedelta(days=2, hours=4),
    11: now - timedelta(days=2, hours=1),
    12: now - timedelta(days=1, hours=5),
    13: now - timedelta(days=1, hours=3),
    14: now - timedelta(hours=8),
    15: now - timedelta(hours=2),
}

for claim in claims:
    ts = timestamps.get(claim.pk)
    if ts:
        # Use raw SQL to bypass auto_now constraints
        connection.cursor().execute(
            "UPDATE claims SET created_at = %s WHERE id = %s",
            [ts, claim.pk]
        )

print('Timestamps updated.')

# Verify top 8 recent claims
print('\nTop 8 recent claims (admin dashboard will show):')
for c in Claim.objects.select_related('claimant','product').order_by('-created_at')[:8]:
    print(f'  {c.claim_reference} | {c.claimant.get_full_name():<18} | {c.product.brand} {c.product.product_name[:18]:<20} | {c.status}')
