from django.contrib import admin
from .models import Claim, ClaimDocument, OCRResult, RepairHistory, ModelPrediction, Review, ModelVersion


@admin.register(ModelVersion)
class ModelVersionAdmin(admin.ModelAdmin):
    list_display  = ['version_name', 'model_type', 'accuracy', 'is_active', 'trained_at']
    list_filter   = ['model_type', 'is_active']


class ClaimDocumentInline(admin.TabularInline):
    model  = ClaimDocument
    extra  = 0
    fields = ['doc_type', 'file', 'file_name', 'file_size', 'uploaded_at']
    readonly_fields = ['uploaded_at']


class RepairHistoryInline(admin.TabularInline):
    model  = RepairHistory
    extra  = 0


@admin.register(Claim)
class ClaimAdmin(admin.ModelAdmin):
    list_display   = ['claim_reference', 'claimant', 'product', 'status', 'final_decision',
                      'python_prediction', 'tm_prediction', 'created_at']
    list_filter    = ['status', 'final_decision', 'damage_type']
    search_fields  = ['claim_reference', 'claimant__email', 'product__serial_number']
    readonly_fields = ['claim_id', 'claim_reference', 'created_at', 'updated_at']
    inlines        = [ClaimDocumentInline, RepairHistoryInline]


@admin.register(ClaimDocument)
class ClaimDocumentAdmin(admin.ModelAdmin):
    list_display  = ['claim', 'doc_type', 'file_name', 'file_size', 'uploaded_at']
    list_filter   = ['doc_type']


@admin.register(OCRResult)
class OCRResultAdmin(admin.ModelAdmin):
    list_display  = ['claim', 'status', 'invoice_number', 'serial_number', 'is_verified', 'extracted_at']
    list_filter   = ['status', 'is_verified', 'ocr_engine']


@admin.register(ModelPrediction)
class ModelPredictionAdmin(admin.ModelAdmin):
    list_display  = ['claim', 'model_type', 'predicted_class', 'top_confidence_pct', 'created_at']
    list_filter   = ['model_type', 'predicted_class']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display  = ['claim', 'reviewer', 'decision', 'is_ai_override', 'reviewed_at']
    list_filter   = ['decision', 'is_ai_override']
