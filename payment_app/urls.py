from django.urls import path
from .views import create_payment, payment_success, payment_cancel, payment_refund

urlpatterns = [
    path("pay/", create_payment, name="create_payment"),
    path("payment/success/", payment_success, name="payment_success"),
    path("payment/cancel/", payment_cancel, name="payment_cancel"),
    path("refund/<int:id>/", payment_refund, name="payment_refund"),
]
