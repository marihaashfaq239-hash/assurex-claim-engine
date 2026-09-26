"""
AssureX — Reviewer app models.
This app primarily uses the Review and Claim models from apps.claims.
No separate tables needed — all review data is stored in claims.Review.
"""
# Models imported lazily to avoid circular imports at Django startup.
# Use: from apps.claims.models import Review, Claim  — in view functions only.
