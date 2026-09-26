"""
AssureX — Claims Models
Tables: 4 (Claims), 5 (Claim_Documents), 6 (OCR_Results),
        7 (Repair_History), 8 (Model_Predictions), 14 (Model_Versions)
"""
import uuid
import hashlib
from django.db import models
from django.utils import timezone
from apps.accounts.models import User
from apps.products.models import Product
from apps.warranties.models import Warranty


# ─────────────────────────────────────────────────────────────────
# Table 14: Model Versions
# ─────────────────────────────────────────────────────────────────
class ModelVersion(models.Model):
    MODEL_TYPES = [
        ('python_ml',        'Python ML Model'),
        ('teachable_machine','Google Teachable Machine'),
    ]

    version_id   = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    model_type   = models.CharField(max_length=30, choices=MODEL_TYPES)
    version_name = models.CharField(max_length=100)
    description  = models.TextField(blank=True)
    file_path    = models.CharField(max_length=500, blank=True)
    accuracy     = models.FloatField(null=True, blank=True)
    is_active    = models.BooleanField(default=True)
    trained_at   = models.DateTimeField(null=True, blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)
    created_by   = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table  = 'model_versions'
        ordering  = ['-created_at']
        verbose_name = 'Model Version'

    def __str__(self):
        return f'{self.get_model_type_display()} v{self.version_name}'

    @classmethod
    def get_active(cls, model_type):
        return cls.objects.filter(model_type=model_type, is_active=True).first()


# ─────────────────────────────────────────────────────────────────
# Table 4: Claims
# ─────────────────────────────────────────────────────────────────
class Claim(models.Model):
    DAMAGE_TYPES = [
        ('physical',      'Physical Damage'),
        ('electrical',    'Electrical Fault'),
        ('mechanical',    'Mechanical Failure'),
        ('software',      'Software Issue'),
        ('manufacturing', 'Manufacturing Defect'),
        ('water',         'Water Damage'),
        ('overheating',   'Overheating'),
        ('battery',       'Battery Issue'),
        ('display',       'Display Problem'),
        ('other',         'Other'),
    ]

    STATUS_CHOICES = [
        ('draft',       'Draft'),
        ('submitted',   'Submitted'),
        ('evaluation',  'Under Evaluation'),
        ('additional',  'Additional Information Required'),
        ('manual',      'Manual Review'),
        ('approved',    'Approved'),
        ('rejected',    'Rejected'),
        ('closed',      'Closed'),
    ]

    FINAL_DECISION = [
        ('likely_valid',    'Likely Valid'),
        ('likely_invalid',  'Likely Invalid'),
        ('manual_review',   'Manual Review Required'),
        ('pending',         'Pending'),
    ]

    # ── IDs ──
    claim_id        = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    claim_reference = models.CharField(max_length=20, unique=True, blank=True,
        help_text='Human-readable reference like CLM-20240001')

    # ── Relationships ──
    claimant        = models.ForeignKey(User, on_delete=models.CASCADE, related_name='claims')
    submitted_by    = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='claims_submitted',
        help_text='Set if submitted by service center employee on behalf of customer'
    )
    product         = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='claims')
    warranty        = models.ForeignKey(Warranty, on_delete=models.PROTECT,
                                        null=True, blank=True, related_name='claims')

    # ── Fault Info ──
    fault_date          = models.DateField(help_text='Date fault was first noticed')
    fault_description   = models.TextField()
    damage_type         = models.CharField(max_length=30, choices=DAMAGE_TYPES)
    fault_location      = models.CharField(max_length=200, blank=True)
    additional_notes    = models.TextField(blank=True)

    # ── Status & Decision ──
    status          = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    final_decision  = models.CharField(max_length=20, choices=FINAL_DECISION, default='pending')
    decision_reason = models.TextField(blank=True)

    # ── AI Evaluation Snapshot ──
    python_prediction       = models.CharField(max_length=30, blank=True)
    python_confidence_valid = models.FloatField(null=True, blank=True)
    python_confidence_invalid = models.FloatField(null=True, blank=True)
    python_confidence_manual = models.FloatField(null=True, blank=True)

    tm_prediction           = models.CharField(max_length=30, blank=True)
    tm_confidence_valid     = models.FloatField(null=True, blank=True)
    tm_confidence_invalid   = models.FloatField(null=True, blank=True)
    tm_confidence_manual    = models.FloatField(null=True, blank=True)

    confidence_difference   = models.FloatField(null=True, blank=True)
    model_consistency_status = models.CharField(max_length=30, blank=True,
        choices=[
            ('strong_match',     'Strong Match'),
            ('acceptable_match', 'Acceptable Match'),
            ('weak_match',       'Weak Match'),
            ('model_disagreement','Model Disagreement'),
            ('uncertain_result', 'Uncertain Result'),
        ])

    # ── Rule Engine Snapshot ──
    rules_passed    = models.PositiveIntegerField(default=0)
    rules_failed    = models.PositiveIntegerField(default=0)
    rules_warning   = models.PositiveIntegerField(default=0)

    # ── Duplicate Detection ──
    is_duplicate    = models.BooleanField(default=False)
    duplicate_of    = models.ForeignKey('self', on_delete=models.SET_NULL,
                                        null=True, blank=True, related_name='duplicates')

    # ── Model Versions used ──
    python_model_version = models.ForeignKey(
        ModelVersion, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='python_predictions'
    )
    tm_model_version = models.ForeignKey(
        ModelVersion, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='tm_predictions'
    )

    # ── Claim Summary Card ──
    claim_card_image = models.ImageField(upload_to='claim_cards/', blank=True, null=True)

    # ── Timestamps ──
    submission_date = models.DateTimeField(null=True, blank=True)
    evaluated_at    = models.DateTimeField(null=True, blank=True)
    closed_at       = models.DateTimeField(null=True, blank=True)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        db_table  = 'claims'
        ordering  = ['-created_at']
        verbose_name = 'Claim'

    def __str__(self):
        return f'Claim {self.claim_reference or str(self.claim_id)[:8]} — {self.claimant}'

    def save(self, *args, **kwargs):
        # Auto-generate human-readable reference
        if not self.claim_reference:
            super().save(*args, **kwargs)
            self.claim_reference = f'CLM-{self.pk:07d}'
            kwargs['update_fields'] = ['claim_reference'] if 'update_fields' not in kwargs else kwargs['update_fields']
        super().save(*args, **kwargs)

    @property
    def is_under_warranty(self):
        if self.warranty:
            return not self.warranty.is_expired
        return False

    @property
    def days_since_fault(self):
        if self.fault_date:
            return (timezone.now().date() - self.fault_date).days
        return None

    @property
    def supporting_documents_count(self):
        return self.documents.count()

    @property
    def missing_document_types(self):
        uploaded = set(self.documents.values_list('doc_type', flat=True))
        required = {'purchase_receipt', 'product_image', 'fault_evidence'}
        return required - uploaded


# ─────────────────────────────────────────────────────────────────
# Table 5: Claim Documents
# ─────────────────────────────────────────────────────────────────
class ClaimDocument(models.Model):
    DOC_TYPES = [
        ('purchase_receipt', 'Purchase Receipt'),
        ('warranty_card',    'Warranty Card'),
        ('product_image',    'Product Image'),
        ('fault_evidence',   'Fault Evidence'),
        ('repair_report',    'Repair Report'),
        ('serial_photo',     'Serial Number Photo'),
        ('diagnostic',       'Diagnostic Report'),
        ('other',            'Other'),
    ]

    doc_id      = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    claim       = models.ForeignKey(Claim, on_delete=models.CASCADE, related_name='documents')
    doc_type    = models.CharField(max_length=30, choices=DOC_TYPES)
    file        = models.FileField(upload_to='claim_documents/%Y/%m/')
    file_name   = models.CharField(max_length=255)
    file_size   = models.PositiveIntegerField(help_text='File size in bytes')
    mime_type   = models.CharField(max_length=100)
    file_hash   = models.CharField(max_length=64, db_index=True,
        help_text='SHA-256 hash for duplicate detection')
    description = models.CharField(max_length=300, blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table  = 'claim_documents'
        ordering  = ['doc_type', '-uploaded_at']
        verbose_name = 'Claim Document'

    def __str__(self):
        return f'{self.get_doc_type_display()} — Claim {self.claim.claim_reference}'

    def save(self, *args, **kwargs):
        # Compute SHA-256 hash on save for duplicate detection
        if self.file and not self.file_hash:
            self.file.seek(0)
            sha256 = hashlib.sha256()
            for chunk in iter(lambda: self.file.read(8192), b''):
                sha256.update(chunk)
            self.file_hash = sha256.hexdigest()
            self.file.seek(0)
        super().save(*args, **kwargs)


# ─────────────────────────────────────────────────────────────────
# Table 6: OCR Results
# ─────────────────────────────────────────────────────────────────
class OCRResult(models.Model):
    OCR_STATUS = [
        ('success',  'Success'),
        ('partial',  'Partial'),
        ('failed',   'Failed'),
    ]

    ocr_id          = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    document        = models.OneToOneField(ClaimDocument, on_delete=models.CASCADE, related_name='ocr_result')
    claim           = models.ForeignKey(Claim, on_delete=models.CASCADE, related_name='ocr_results')

    # ── Extracted Fields ──
    invoice_number  = models.CharField(max_length=100, blank=True)
    product_name    = models.CharField(max_length=200, blank=True)
    brand           = models.CharField(max_length=100, blank=True)
    model_number    = models.CharField(max_length=100, blank=True)
    serial_number   = models.CharField(max_length=200, blank=True)
    purchase_date   = models.DateField(null=True, blank=True)
    purchase_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    retailer        = models.CharField(max_length=200, blank=True)
    warranty_duration = models.CharField(max_length=50, blank=True)

    # ── Raw & Status ──
    raw_text        = models.TextField(blank=True)
    extracted_data  = models.JSONField(default=dict, blank=True)
    status          = models.CharField(max_length=10, choices=OCR_STATUS, default='success')
    confidence      = models.FloatField(null=True, blank=True, help_text='OCR confidence 0-1')
    ocr_engine      = models.CharField(max_length=50, default='tesseract')

    # ── Verification ──
    is_verified         = models.BooleanField(default=False)
    verified_by         = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    verification_notes  = models.TextField(blank=True)

    extracted_at = models.DateTimeField(auto_now_add=True)
    verified_at  = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table  = 'ocr_results'
        verbose_name = 'OCR Result'

    def __str__(self):
        return f'OCR [{self.status}] — {self.document}'


# ─────────────────────────────────────────────────────────────────
# Table 7: Repair History
# ─────────────────────────────────────────────────────────────────
class RepairHistory(models.Model):
    REPAIR_OUTCOMES = [
        ('fixed',       'Fixed'),
        ('partial',     'Partially Fixed'),
        ('failed',      'Repair Failed'),
        ('replaced',    'Component Replaced'),
        ('pending',     'Pending'),
    ]

    repair_id       = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    claim           = models.ForeignKey(Claim, on_delete=models.CASCADE, related_name='repair_history')
    product         = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='repair_history')

    repair_date         = models.DateField()
    repair_center       = models.CharField(max_length=200)
    is_authorized       = models.BooleanField(default=True,
        help_text='Whether repaired by authorized service center')
    replaced_parts      = models.TextField(blank=True)
    repair_description  = models.TextField()
    repair_cost         = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    outcome             = models.CharField(max_length=20, choices=REPAIR_OUTCOMES)
    repair_report_file  = models.FileField(upload_to='repair_reports/', blank=True, null=True)

    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table  = 'repair_history'
        ordering  = ['-repair_date']
        verbose_name = 'Repair History'
        verbose_name_plural = 'Repair Histories'

    def __str__(self):
        auth = 'Authorized' if self.is_authorized else 'Unauthorized'
        return f'{auth} repair on {self.repair_date} at {self.repair_center}'


# ─────────────────────────────────────────────────────────────────
# Table 8: Model Predictions
# ─────────────────────────────────────────────────────────────────
class ModelPrediction(models.Model):
    MODEL_TYPES = [
        ('python_ml',        'Python ML Model'),
        ('teachable_machine','Google Teachable Machine'),
    ]

    PREDICTION_CLASSES = [
        ('valid_claim',    'Valid Claim'),
        ('invalid_claim',  'Invalid Claim'),
        ('manual_review',  'Manual Review'),
    ]

    prediction_id   = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    claim           = models.ForeignKey(Claim, on_delete=models.CASCADE, related_name='predictions')
    model_type      = models.CharField(max_length=30, choices=MODEL_TYPES)
    model_version   = models.ForeignKey(ModelVersion, on_delete=models.SET_NULL,
                                         null=True, related_name='predictions')

    # ── Prediction ──
    predicted_class         = models.CharField(max_length=20, choices=PREDICTION_CLASSES)
    confidence_valid        = models.FloatField(help_text='Confidence for Valid Claim (0-1)')
    confidence_invalid      = models.FloatField(help_text='Confidence for Invalid Claim (0-1)')
    confidence_manual_review = models.FloatField(help_text='Confidence for Manual Review (0-1)')

    # Input snapshot (JSON serialization of what was fed to the model)
    input_data      = models.JSONField(default=dict, blank=True)

    # Processing time
    processing_time_ms = models.PositiveIntegerField(null=True, blank=True)

    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table  = 'model_predictions'
        ordering  = ['-created_at']
        verbose_name = 'Model Prediction'

    def __str__(self):
        return (f'{self.get_model_type_display()} → {self.predicted_class} '
                f'({self.top_confidence:.1%})')

    @property
    def top_confidence(self):
        """Confidence of the predicted class."""
        mapping = {
            'valid_claim':   self.confidence_valid,
            'invalid_claim': self.confidence_invalid,
            'manual_review': self.confidence_manual_review,
        }
        return mapping.get(self.predicted_class, 0.0)

    @property
    def top_confidence_pct(self):
        return round(self.top_confidence * 100, 2)


# ─────────────────────────────────────────────────────────────────
# Table 11: Reviews (Reviewer decisions)
# ─────────────────────────────────────────────────────────────────
class Review(models.Model):
    REVIEW_DECISIONS = [
        ('approved',    'Approved'),
        ('rejected',    'Rejected'),
        ('more_info',   'Additional Information Requested'),
        ('pending',     'Pending'),
    ]

    review_id       = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    claim           = models.OneToOneField(Claim, on_delete=models.CASCADE, related_name='review')
    reviewer        = models.ForeignKey(User, on_delete=models.SET_NULL,
                                         null=True, related_name='reviews')

    # ── AI Results shown to reviewer ──
    python_prediction   = models.CharField(max_length=30, blank=True)
    tm_prediction       = models.CharField(max_length=30, blank=True)
    model_consistency   = models.CharField(max_length=30, blank=True)

    # ── Reviewer Decision ──
    decision            = models.CharField(max_length=20, choices=REVIEW_DECISIONS, default='pending')
    reviewer_comments   = models.TextField()
    additional_info_request = models.TextField(blank=True,
        help_text='Filled if decision is more_info')

    # ── Override ──
    is_ai_override      = models.BooleanField(default=False)
    ai_original_result  = models.CharField(max_length=30, blank=True)
    override_reason     = models.TextField(blank=True)

    # ── Timestamps ──
    assigned_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table  = 'reviews'
        ordering  = ['-assigned_at']
        verbose_name = 'Review'

    def __str__(self):
        return f'Review of {self.claim} — {self.decision}'
