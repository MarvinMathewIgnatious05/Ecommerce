
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
    payer_id = request.GET.get("PayerID")

    try:
        payment = paypalrestsdk.Payment.find(payment_id)
        if payment.execute({"payer_id": payer_id}):
            # Find the sale ID from the transaction
            sale_id = None
            for transaction in payment.transactions:
                for resource in transaction.related_resources:
                    if 'sale' in resource:
                        sale_id = resource['sale']['id']
                        break

            # Update the database with the sale ID
            db_payment = Payment.objects.get(paypal_payment_id=payment_id)
            db_payment.status = "COMPLETED"
            db_payment.paypal_sale_id = sale_id  # Store Sale ID
            db_payment.save()

            return render(request, "payment_success.html", {
                            "payment_id": db_payment.paypal_payment_id,
                            "sale_id": db_payment.paypal_sale_id,  # Show in template
                            "amount": db_payment.amount
                        })
        else:
            return render(request, "error.html", {"error": "Payment execution failed."})

    except Payment.DoesNotExist:
        return render(request, "error.html", {"error": "Payment not found."})





# def payment_success(request):
#     payment_id = request.GET.get("paymentId")
#     payment = Payment.objects.get(paypal_payment_id=payment_id)
#
#     if payment:
#         payment.status = "COMPLETED"
#         payment.save()
#         return render(request, "payment_success.html")
#
#     return render(request, "error.html", {"error": "Invalid Payment ID"})


def payment_cancel(request):
    return render(request, "payment_cancel.html")








# Refund Payment View
def refund_payment(request, payment_id):
    try:
        payment = Payment.objects.get(paypal_payment_id=payment_id)
        if payment.status != "COMPLETED":
            return render(request, "error.html", {"error": "Only completed payments can be refunded."})

        sale_id = None
        paypal_payment = paypalrestsdk.Payment.find(payment_id)

        for transaction in paypal_payment.transactions:
            for related_resource in transaction.related_resources:
                if 'sale' in related_resource:
                    sale_id = related_resource['sale']['id']
                    break

        if not sale_id:
            return render(request, "error.html", {"error": "Sale ID not found for refund."})

        sale = paypalrestsdk.Sale.find(sale_id)
        refund = sale.refund({
            "amount": {
                "total": str(payment.amount),  # Ensure total is a string
                "currency": "USD"
            }
        })


        if refund.success():
            payment.status = "REFUNDED"
            payment.save()
            return render(request, "refund_success.html")
        else:
            return render(request, "error.html", {"error": refund.error})

    except Payment.DoesNotExist:
        return render(request, "error.html", {"error": "Payment not found."})

