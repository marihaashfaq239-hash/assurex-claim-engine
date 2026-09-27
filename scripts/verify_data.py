from apps.claims.models import Claim
from apps.accounts.models import User

emp = User.objects.get(email='employee@assurex.com')
all_c = Claim.objects.all()

print('=== ADMIN DASHBOARD STATS ===')
print('Total Claims      :', all_c.count())
print('Likely Valid       :', all_c.filter(final_decision='likely_valid').count())
print('Likely Invalid     :', all_c.filter(final_decision='likely_invalid').count())
print('Manual Review      :', all_c.filter(status='manual').count())
print('Approved           :', all_c.filter(status='approved').count())
print('Rejected           :', all_c.filter(status='rejected').count())
print('Pending/Evaluation :', all_c.filter(status__in=['submitted','evaluation']).count())
print('Model Disagreements:', all_c.filter(model_consistency_status__in=['model_disagreement','uncertain_result']).count())

print()
print('=== EMPLOYEE DASHBOARD STATS ===')
emp_c = Claim.objects.filter(submitted_by=emp)
print('Total Created  :', emp_c.count())
print('Approved       :', emp_c.filter(status='approved').count())
print('Active/Pending :', emp_c.filter(status__in=['submitted','evaluation','manual']).count())

print()
print('=== ALL CLAIMS ===')
for c in all_c.order_by('pk'):
    tag = ' [emp: ' + c.submitted_by.first_name + ']' if c.submitted_by else ''
    print(' ', c.claim_reference, '|', c.product.brand.ljust(8),
          '|', c.status.ljust(12), '|', c.final_decision.ljust(15) + tag)
