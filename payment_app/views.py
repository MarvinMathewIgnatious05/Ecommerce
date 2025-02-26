
import paypalrestsdk
from django.conf import settings
from django.shortcuts import render, redirect
from shopping_cart_app.models import Cart
from .models import Payment
from django.http import HttpResponse
from product_management_app.models import Product











# Configure PayPal
paypalrestsdk.configure({
    "mode": settings.PAYPAL_MODE,
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET
})


def create_payment(request):
    user = request.user
    cart_items = Cart.objects.filter(user=user)
    total_price = sum(item.product_id.price * item.quantity for item in cart_items)

    # Create a PayPal payment
    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"
        },
        "redirect_urls": {
            "return_url": request.build_absolute_uri("/payment/success/"),
            "cancel_url": request.build_absolute_uri("/payment/cancel/")
        },
        "transactions": [{
            "amount": {
                "total": str(total_price),
                "currency": "USD"
            },
            "description": "E-commerce Purchase"
        }]
    })

    if payment.create():
        payment_instance = Payment.objects.create(
            user=user,
            amount=total_price,
            paypal_payment_id=payment.id,
            status="PENDING",
        )
        payment_instance.product.set([item.product_id for item in cart_items])
        payment_instance.save()

        for link in payment.links:
            if link.rel == "approval_url":
                return redirect(link.href)
    else:
        return render(request, "error.html", {"error": payment.error})


def payment_success(request):
    payment_id = request.GET.get("paymentId")
    payment = Payment.objects.get(paypal_payment_id=payment_id)

    if payment:
        payment.status = "COMPLETED"
        payment.save()
        return render(request, "success.html")

    return render(request, "error.html", {"error": "Invalid Payment ID"})


def payment_cancel(request):
    return render(request, "cancel.html")






def payment_refund(request, id):
    payment = Payment.objects.filter(paypal_payment_id=id).first()

    if not payment:
        return HttpResponse("<h2>Payment not found</h2>", content_type="text/html")

    if payment.status != "COMPLETED":
        return HttpResponse("<h2>Payment is not completed</h2>", content_type="text/html")

    if not payment.paypal_sale_id:
        return HttpResponse("<h2>Sale ID not found</h2>", content_type="text/html")

    sale = paypalrestsdk.Sale.find(payment.paypal_sale_id)
    refund = sale.refund({
        "amount": {
            "total": str(payment.amount),
            "currency": "USD"
        }
    })

    if refund.success():
        payment.status = "REFUNDED"
        payment.save()
        return HttpResponse("<h2>Refund successful</h2>", content_type="text/html")

    return HttpResponse("<h2>Refund failed</h2>", content_type="text/html")


