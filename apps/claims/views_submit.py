"""
AssureX — Claim Submission Workflow (Customer & Employee)
Multi-step wizard:
  Step 1 — Select product & enter fault info
  Step 2 — Upload documents (receipt, warranty card, evidence)
  Step 3 — Add repair history (optional)
  Step 4 — Review & submit → triggers OCR + validation + AI pipeline
"""
from __future__ import annotations
import os
import hashlib
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from .models import Claim, ClaimDocument, OCRResult, RepairHistory
from .forms import ClaimSubmitForm, DocumentUploadForm, RepairHistoryForm
from apps.accounts.models import AuditLog
from apps.products.models import Product
from apps.warranties.models import Warranty
from apps.notifications.models import Notification

logger = logging.getLogger(__name__)


def _log(request, action, desc, obj_type='', obj_id=''):
    ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', ''))
    if ',' in ip:
        ip = ip.split(',')[0].strip()
    AuditLog.objects.create(
        user=request.user, action_type=action, description=desc,
        ip_address=ip or None, object_type=obj_type, object_id=str(obj_id),
    )


def _compute_hash(file_obj) -> str:
    """SHA-256 hash of an uploaded file for duplicate detection."""
    sha256 = hashlib.sha256()
    file_obj.seek(0)
    for chunk in iter(lambda: file_obj.read(8192), b''):
        sha256.update(chunk)
    file_obj.seek(0)
    return sha256.hexdigest()


def _check_duplicate_document(file_hash: str, current_claim_id=None) -> bool:
    """Returns True if this file hash already exists in another claim."""
    qs = ClaimDocument.objects.filter(file_hash=file_hash)
    if current_claim_id:
        qs = qs.exclude(claim_id=current_claim_id)
    return qs.exists()


def _run_ocr_on_document(doc: ClaimDocument):
    """
    Run OCR extraction on a document and save the result.
    Gracefully continues if OCR library is not installed.
    """
    try:
        from src.ocr.extractor import extract_document_data
        file_path = doc.file.path
        result    = extract_document_data(file_path)

        OCRResult.objects.update_or_create(
            document=doc,
            defaults={
                'claim':            doc.claim,
                'invoice_number':   result.get('invoice_number') or '',
                'serial_number':    result.get('serial_number') or '',
                'model_number':     result.get('model_number') or '',
                'purchase_date':    _parse_date_safe(result.get('purchase_date')),
                'purchase_amount':  result.get('purchase_amount'),
                'retailer':         result.get('retailer') or '',
                'warranty_duration':result.get('warranty_duration') or '',
                'raw_text':         result.get('raw_text') or '',
                'extracted_data':   result,
                'status':           'success' if result.get('confidence', 0) > 0.3 else 'partial',
                'confidence':       result.get('confidence', 0),
                'ocr_engine':       result.get('engine', 'none'),
            }
        )
        logger.info(f'OCR completed for document {doc.pk}, confidence={result.get("confidence")}')
    except Exception as e:
        logger.warning(f'OCR failed for document {doc.pk}: {e}')
        OCRResult.objects.get_or_create(
            document=doc,
            defaults={'claim': doc.claim, 'status': 'failed', 'raw_text': str(e)}
        )


def _parse_date_safe(date_str):
    """Parse ISO date string to date object, returns None on failure."""
    if not date_str:
        return None
    try:
        from datetime import datetime
        return datetime.strptime(date_str[:10], '%Y-%m-%d').date()
    except Exception:
        return None


def _detect_contradictions(claim: Claim) -> list[dict]:
    """
    SRS §1.6.xxviii — Contradiction Detection.

    Checks for conflicting information across claim fields, OCR-extracted data,
    repair history, warranty records, and product registration data.

    Returns a list of contradiction dicts:
        {
            'type':        str,   # contradiction category
            'severity':    str,   # 'hard' | 'warning'
            'description': str,   # human-readable explanation
        }

    Hard contradictions → claim should be sent to Manual Review.
    Warning contradictions → flagged but do not block submission.
    """
    contradictions = []
    today          = timezone.now().date()
    product        = claim.product
    ocr_results    = list(claim.ocr_results.all())
    repair_history = list(claim.repair_history.all())
    warranty       = claim.warranty

    # ── C1: Fault date before purchase date ──────────────────────
    if claim.fault_date and product.purchase_date:
        if claim.fault_date < product.purchase_date:
            contradictions.append({
                'type':        'fault_before_purchase',
                'severity':    'hard',
                'description': (
                    f'Fault date ({claim.fault_date}) is before the product purchase date '
                    f'({product.purchase_date}). A fault cannot occur before the product was purchased.'
                ),
            })

    # ── C2: Fault date in the future ─────────────────────────────
    if claim.fault_date and claim.fault_date > today:
        contradictions.append({
            'type':        'fault_date_future',
            'severity':    'hard',
            'description': (
                f'Fault date ({claim.fault_date}) is in the future. '
                f'Please enter the actual date the fault was first noticed.'
            ),
        })

    # ── C3: Repair date before purchase date ─────────────────────
    for repair in repair_history:
        if repair.repair_date and product.purchase_date:
            if repair.repair_date < product.purchase_date:
                contradictions.append({
                    'type':        'repair_before_purchase',
                    'severity':    'hard',
                    'description': (
                        f'Repair at "{repair.repair_center}" on {repair.repair_date} '
                        f'is recorded before the product purchase date ({product.purchase_date}).'
                    ),
                })
        # ── C4: Repair date after claim submission ────────────────
        if repair.repair_date and repair.repair_date > today:
            contradictions.append({
                'type':        'repair_date_future',
                'severity':    'warning',
                'description': (
                    f'Repair date at "{repair.repair_center}" ({repair.repair_date}) '
                    f'is set in the future.'
                ),
            })
        # ── C5: Repair date after fault date ─────────────────────
        if repair.repair_date and claim.fault_date:
            if repair.repair_date < claim.fault_date:
                # Repair happened BEFORE the reported fault — suspicious
                contradictions.append({
                    'type':        'repair_before_fault',
                    'severity':    'warning',
                    'description': (
                        f'A repair at "{repair.repair_center}" on {repair.repair_date} '
                        f'is recorded before the reported fault date ({claim.fault_date}). '
                        f'Please verify the dates are correct.'
                    ),
                })

    # ── C6: OCR serial number mismatch with product serial ────────
    for ocr in ocr_results:
        if ocr.serial_number and product.serial_number:
            ocr_sn  = ocr.serial_number.strip().upper().replace('-', '').replace(' ', '')
            prod_sn = product.serial_number.strip().upper().replace('-', '').replace(' ', '')
            if ocr_sn and prod_sn and ocr_sn != prod_sn:
                contradictions.append({
                    'type':        'serial_number_mismatch',
                    'severity':    'hard',
                    'description': (
                        f'Serial number on document ({ocr.serial_number}) does not match '
                        f'the registered product serial number ({product.serial_number}). '
                        f'Please upload the correct documents or update the product serial number.'
                    ),
                })

    # ── C7: OCR purchase date does not match product purchase date ─
    for ocr in ocr_results:
        if ocr.purchase_date and product.purchase_date:
            if ocr.purchase_date != product.purchase_date:
                contradictions.append({
                    'type':        'purchase_date_mismatch',
                    'severity':    'warning',
                    'description': (
                        f'Purchase date extracted from document ({ocr.purchase_date}) '
                        f'does not match the registered product purchase date '
                        f'({product.purchase_date}). Please verify the receipt is for this product.'
                    ),
                })

    # ── C8: OCR model number mismatch ─────────────────────────────
    for ocr in ocr_results:
        if ocr.model_number and product.model_number:
            ocr_mn  = ocr.model_number.strip().upper().replace(' ', '')
            prod_mn = product.model_number.strip().upper().replace(' ', '')
            if ocr_mn and prod_mn and ocr_mn != prod_mn:
                contradictions.append({
                    'type':        'model_number_mismatch',
                    'severity':    'warning',
                    'description': (
                        f'Model number on document ({ocr.model_number}) does not match '
                        f'the registered product model number ({product.model_number}).'
                    ),
                })

    # ── C9: Warranty already expired at time of fault ─────────────
    if warranty and claim.fault_date:
        if warranty.expiry_date < claim.fault_date:
            contradictions.append({
                'type':        'warranty_expired_at_fault',
                'severity':    'hard',
                'description': (
                    f'The warranty expired on {warranty.expiry_date}, but the fault was '
                    f'reported on {claim.fault_date}. This claim falls outside the warranty period.'
                ),
            })

    # ── C10: Inconsistent product models across OCR docs ──────────
    model_numbers_from_ocr = [
        ocr.model_number.strip().upper()
        for ocr in ocr_results
        if ocr.model_number and ocr.model_number.strip()
    ]
    unique_models = set(model_numbers_from_ocr)
    if len(unique_models) > 1:
        contradictions.append({
            'type':        'inconsistent_ocr_models',
            'severity':    'warning',
            'description': (
                f'Multiple different model numbers found across uploaded documents: '
                f'{", ".join(unique_models)}. Please ensure all documents belong to the same product.'
            ),
        })

    # ── C11: Multiple serial numbers across OCR docs ──────────────
    serial_numbers_from_ocr = [
        ocr.serial_number.strip().upper().replace('-', '').replace(' ', '')
        for ocr in ocr_results
        if ocr.serial_number and ocr.serial_number.strip()
    ]
    unique_serials = set(serial_numbers_from_ocr)
    if len(unique_serials) > 1:
        contradictions.append({
            'type':        'inconsistent_ocr_serials',
            'severity':    'warning',
            'description': (
                f'Multiple different serial numbers found across uploaded documents. '
                f'Please ensure all documents are for the same product unit.'
            ),
        })

    return contradictions


def _validate_claim_data(claim: Claim) -> list[str]:
    """
    Pre-submission validation: returns list of error/warning messages.
    Includes SRS §1.6.xv (Data Validation) and §1.6.xxviii (Contradiction Detection).
    """
    errors = []

    # ── Mandatory fields ──
    if not claim.fault_description.strip():
        errors.append('Fault description is required.')
    if not claim.fault_date:
        errors.append('Fault date is required.')

    # ── Duplicate claim check ──
    product  = claim.product
    existing = Claim.objects.filter(
        product=product,
        claimant=claim.claimant,
        status__in=['submitted', 'evaluation', 'manual', 'additional'],
    ).exclude(pk=claim.pk)
    if existing.exists():
        claim.is_duplicate = True
        claim.save(update_fields=['is_duplicate'])
        errors.append(
            'Warning: A similar open claim exists for this product. '
            'Your claim has been flagged for duplicate review.'
        )

    # ── Contradiction detection (SRS §1.6.xxviii) ──
    contradictions = _detect_contradictions(claim)
    for c in contradictions:
        prefix = '' if c['severity'] == 'hard' else 'Warning: '
        errors.append(f'{prefix}[Contradiction] {c["description"]}')

    # Persist contradiction count to claim for the AI pipeline
    hard_count    = sum(1 for c in contradictions if c['severity'] == 'hard')
    warn_count    = sum(1 for c in contradictions if c['severity'] == 'warning')
    if contradictions:
        # Store as JSON on the claim so the AI engine can use it
        import json
        from apps.accounts.models import AuditLog
        AuditLog.objects.create(
            user=claim.claimant,
            action_type='claim_created',
            description=(
                f'Contradiction check for {claim.claim_reference}: '
                f'{hard_count} hard, {warn_count} warnings.'
            ),
            object_type='Claim',
            object_id=str(claim.pk),
            extra_data={'contradictions': contradictions},
        )

    return errors


def _trigger_ai_pipeline(claim: Claim):
    """
    Trigger the full AI evaluation pipeline after claim submission.
    Runs: preprocessing → Python ML → Teachable Machine → rule engine → decision.
    This is called async-style; if it fails the claim stays in 'evaluation' status.
    """
    try:
        from src.decision_engine.evaluator import evaluate_claim
        evaluate_claim(claim)
    except Exception as e:
        logger.error(f'AI pipeline failed for claim {claim.claim_reference}: {e}')
        # Keep claim in evaluation status — admin will see it in monitoring


# ─────────────────────────────────────────────────────────────────
# STEP 1 — Claim Info
# ─────────────────────────────────────────────────────────────────

@login_required
def claim_submit_step1(request):
    """
    Step 1: Select product, enter fault details.
    Saves a Draft claim and redirects to step 2.
    Pre-populates product if ?product=pk is in URL.
    """
    product_pk = request.GET.get('product') or request.POST.get('product')
    user = request.user

    # Scope products to this customer's registered products
    form = ClaimSubmitForm(request.POST or None, user=user)

    if request.method == 'POST' and form.is_valid():
        claim = form.save(commit=False)
        claim.claimant = user
        claim.status   = 'draft'
        claim.save()

        _log(request, 'claim_created',
             f'Draft claim created by {user.email} for product {claim.product.serial_number}',
             'Claim', claim.pk)
        return redirect('claims:submit_step2', pk=claim.pk)

    # Pre-select product if given
    if product_pk:
        try:
            initial_product = Product.objects.get(pk=product_pk, owner=user)
            form.fields['product'].initial = initial_product
            form.fields['warranty'].queryset = Warranty.objects.filter(product=initial_product)
        except Product.DoesNotExist:
            pass

    context = {
        'form':       form,
        'page_title': 'Submit Claim — Step 1: Fault Details',
        'step':       1,
    }
    return render(request, 'claims/submit_step1.html', context)


# ─────────────────────────────────────────────────────────────────
# STEP 2 — Document Upload
# ─────────────────────────────────────────────────────────────────

@login_required
def claim_submit_step2(request, pk):
    """
    Step 2: Upload supporting documents.
    Runs OCR on each uploaded document immediately.
    """
    claim = get_object_or_404(Claim, pk=pk, claimant=request.user, status='draft')

    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.claim      = claim
            doc.uploaded_by = request.user
            # Set file metadata
            f = request.FILES.get('file')
            if f:
                doc.file_name  = f.name
                doc.file_size  = f.size
                doc.mime_type  = getattr(f, 'content_type', 'application/octet-stream')
                doc.file_hash  = _compute_hash(f)
                # Check duplicate document
                if _check_duplicate_document(doc.file_hash, current_claim_id=claim.pk):
                    messages.warning(
                        request,
                        f'Warning: {f.name} appears to have been used in another claim. It has been uploaded but flagged.'
                    )
            doc.save()

            # Run OCR on image/PDF documents
            if doc.doc_type in ('purchase_receipt', 'warranty_card', 'repair_report'):
                _run_ocr_on_document(doc)
                messages.success(request, f'{doc.get_doc_type_display()} uploaded and OCR extraction complete.')
            else:
                messages.success(request, f'{doc.get_doc_type_display()} uploaded successfully.')

            _log(request, 'document_uploaded',
                 f'Document {doc.doc_type} uploaded for claim {claim.claim_reference}',
                 'ClaimDocument', doc.pk)
            return redirect('claims:submit_step2', pk=pk)
        else:
            messages.error(request, 'Upload failed. Please check the file type and size (max 5MB).')

    else:
        form = DocumentUploadForm()

    documents    = claim.documents.all()
    ocr_results  = {ocr.document_id: ocr for ocr in claim.ocr_results.all()}
    uploaded_types = set(documents.values_list('doc_type', flat=True))
    missing        = claim.missing_document_types

    context = {
        'claim':          claim,
        'form':           form,
        'documents':      documents,
        'ocr_results':    ocr_results,
        'uploaded_types': uploaded_types,
        'missing':        missing,
        'page_title':     f'Submit Claim — Step 2: Documents',
        'step':           2,
    }
    return render(request, 'claims/submit_step2.html', context)


# ─────────────────────────────────────────────────────────────────
# STEP 3 — Repair History
# ─────────────────────────────────────────────────────────────────

@login_required
def claim_submit_step3(request, pk):
    """
    Step 3: Add previous repair history (optional).
    Each repair entry is saved independently.
    """
    claim = get_object_or_404(Claim, pk=pk, claimant=request.user, status='draft')

    if request.method == 'POST':
        if 'add_repair' in request.POST:
            form = RepairHistoryForm(request.POST)
            if form.is_valid():
                repair = form.save(commit=False)
                repair.claim   = claim
                repair.product = claim.product
                repair.save()
                messages.success(request, 'Repair record added.')
                return redirect('claims:submit_step3', pk=pk)
            else:
                messages.error(request, 'Please correct the repair form errors.')
        elif 'next_step' in request.POST:
            return redirect('claims:submit_step4', pk=pk)

    else:
        form = RepairHistoryForm()

    repairs = claim.repair_history.all()
    context = {
        'claim':    claim,
        'form':     form,
        'repairs':  repairs,
        'page_title': f'Submit Claim — Step 3: Repair History',
        'step':     3,
    }
    return render(request, 'claims/submit_step3.html', context)


@login_required
def delete_repair(request, claim_pk, repair_pk):
    """Remove a repair history entry."""
    claim  = get_object_or_404(Claim, pk=claim_pk, claimant=request.user, status='draft')
    repair = get_object_or_404(RepairHistory, pk=repair_pk, claim=claim)
    repair.delete()
    messages.success(request, 'Repair record removed.')
    return redirect('claims:submit_step3', pk=claim_pk)


# ─────────────────────────────────────────────────────────────────
# STEP 4 — Review & Submit
# ─────────────────────────────────────────────────────────────────

@login_required
def claim_submit_step4(request, pk):
    """
    Step 4: Summary review + final submission.
    On GET:  runs contradiction detection for preview (SRS §1.6.xxxiii — Claim Preparation Assistance).
    On POST: validates → changes status to submitted → triggers AI pipeline.
    """
    claim = get_object_or_404(Claim, pk=pk, claimant=request.user, status='draft')

    documents   = claim.documents.all()
    ocr_results = claim.ocr_results.all()
    repairs     = claim.repair_history.all()

    if request.method == 'POST':
        # Full validation including contradiction detection
        validation_errors = _validate_claim_data(claim)

        # Separate hard errors from warnings
        hard_errors = [e for e in validation_errors if not e.startswith('Warning')]
        warnings    = [e for e in validation_errors if e.startswith('Warning')]

        if hard_errors:
            for err in hard_errors:
                messages.error(request, err)
            for warn in warnings:
                messages.warning(request, warn)
            return redirect('claims:submit_step4', pk=pk)

        for warn in warnings:
            messages.warning(request, warn)

        # Submit the claim
        claim.status          = 'submitted'
        claim.submission_date = timezone.now()
        claim.save(update_fields=['status', 'submission_date', 'updated_at', 'is_duplicate'])

        _log(request, 'claim_submitted',
             f'Claim {claim.claim_reference} submitted by {request.user.email}',
             'Claim', claim.pk)

        # Notify customer
        Notification.send(
            recipient=request.user,
            notification_type='claim_submitted',
            title=f'Claim {claim.claim_reference} Submitted',
            message='Your claim has been submitted and is now under evaluation.',
            link=f'/claims/{claim.pk}/',
            object_type='Claim', object_id=claim.pk,
        )

        # Move to evaluation and trigger AI pipeline
        claim.status = 'evaluation'
        claim.save(update_fields=['status', 'updated_at'])
        _trigger_ai_pipeline(claim)

        messages.success(
            request,
            f'Claim {claim.claim_reference} submitted successfully! '
            f'Our AI engine is evaluating your claim. '
            f'You will be notified once the result is ready.'
        )
        return redirect('claims:detail', pk=claim.pk)

    # OCR verification data — show extracted fields for each OCR'd document
    ocr_map = {ocr.document_id: ocr for ocr in ocr_results}

    # ── Pre-check contradictions for the review page (SRS §1.6.xxxiii) ──
    # Run on GET so user sees issues BEFORE hitting submit.
    pre_contradictions = _detect_contradictions(claim)
    hard_contradictions   = [c for c in pre_contradictions if c['severity'] == 'hard']
    warn_contradictions   = [c for c in pre_contradictions if c['severity'] == 'warning']

    context = {
        'claim':               claim,
        'documents':           documents,
        'ocr_results':         ocr_results,
        'ocr_map':             ocr_map,
        'repairs':             repairs,
        'missing':             claim.missing_document_types,
        'contradictions':      pre_contradictions,
        'hard_contradictions': hard_contradictions,
        'warn_contradictions': warn_contradictions,
        'page_title':          'Submit Claim — Step 4: Review & Submit',
        'step':                4,
    }
    return render(request, 'claims/submit_step4.html', context)


# ─────────────────────────────────────────────────────────────────
# OCR Verification — user can correct extracted data
# ─────────────────────────────────────────────────────────────────

@login_required
def verify_ocr(request, claim_pk, ocr_pk):
    """
    Allow user to review and correct OCR-extracted data before submission.
    """
    claim = get_object_or_404(Claim, pk=claim_pk, claimant=request.user, status='draft')
    ocr   = get_object_or_404(OCRResult, pk=ocr_pk, claim=claim)

    if request.method == 'POST':
        ocr.invoice_number  = request.POST.get('invoice_number', ocr.invoice_number)
        ocr.serial_number   = request.POST.get('serial_number', ocr.serial_number)
        ocr.model_number    = request.POST.get('model_number', ocr.model_number)
        ocr.retailer        = request.POST.get('retailer', ocr.retailer)
        ocr.warranty_duration = request.POST.get('warranty_duration', ocr.warranty_duration)

        # Parse purchase_date
        pd_str = request.POST.get('purchase_date', '')
        if pd_str:
            ocr.purchase_date = _parse_date_safe(pd_str)

        pa_str = request.POST.get('purchase_amount', '')
        if pa_str:
            try:
                ocr.purchase_amount = float(pa_str)
            except ValueError:
                pass

        ocr.is_verified         = True
        ocr.verified_by         = request.user
        ocr.verified_at         = timezone.now()
        ocr.verification_notes  = request.POST.get('notes', '')
        ocr.save()

        _log(request, 'data_corrected',
             f'OCR data corrected for document in claim {claim.claim_reference}',
             'OCRResult', ocr.pk)
        messages.success(request, 'OCR data updated and verified.')
        return redirect('claims:submit_step2', pk=claim_pk)

    context = {
        'claim': claim,
        'ocr':   ocr,
        'page_title': 'Verify Extracted Data',
    }
    return render(request, 'claims/verify_ocr.html', context)
