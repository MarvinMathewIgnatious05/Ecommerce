from django.urls import path
from .views import create_payment, payment_success, payment_cancel, refund_payment, bill_receipt

urlpatterns = [
    path("pay/", create_payment, name="create_payment"),
    path("payment/success/", payment_success, name="payment_success"),
    path("payment/cancel/", payment_cancel, name="payment_cancel"),
    path("payment/refund/<str:payment_id>/", refund_payment, name="payment_refund"),
    path('payment/receipt/<str:payment_id>/', bill_receipt, name='bill_receipt'),

]
