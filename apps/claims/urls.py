from django.urls import path
from .views_customer import my_claims, claim_detail, download_claim_report
from .views_employee import (
    employee_dashboard, customer_search, customer_detail_employee,
    employee_claim_list, employee_create_claim, customer_products_ajax,
)
from .views_submit import (
    claim_submit_step1, claim_submit_step2, claim_submit_step3,
    claim_submit_step4, delete_repair, verify_ocr,
)

app_name = 'claims'

urlpatterns = [
    # ── Customer ──
    path('my/',                       my_claims,               name='my_claims'),
    path('<int:pk>/',                  claim_detail,            name='detail'),
    path('<int:pk>/report/',           download_claim_report,   name='download_report'),

    # ── Submission wizard ──
    path('submit/',                    claim_submit_step1,      name='submit'),
    path('<int:pk>/documents/',        claim_submit_step2,      name='submit_step2'),
    path('<int:pk>/repairs/',          claim_submit_step3,      name='submit_step3'),
    path('<int:pk>/review/',           claim_submit_step4,      name='submit_step4'),
    path('<int:claim_pk>/repairs/<int:repair_pk>/delete/', delete_repair, name='delete_repair'),
    path('<int:claim_pk>/ocr/<int:ocr_pk>/verify/', verify_ocr, name='verify_ocr'),

    # ── Employee ──
    path('employee/',                  employee_claim_list,     name='employee_list'),
    path('employee/create/',           employee_create_claim,   name='employee_create'),
    path('customer/search/',           customer_search,         name='customer_search'),
    path('customer/<int:customer_pk>/',customer_detail_employee,name='customer_detail'),
    path('ajax/customer-products/',    customer_products_ajax,  name='customer_products_ajax'),
]
