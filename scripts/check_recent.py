from apps.claims.models import Claim
print('Top 8 recent claims:')
for c in Claim.objects.select_related('claimant','product').order_by('-created_at')[:8]:
    print('  ', c.claim_reference, '|', c.claimant.get_full_name(), '|',
          c.product.brand, '|', c.status, '|', c.created_at.strftime('%b %d %H:%M'))
