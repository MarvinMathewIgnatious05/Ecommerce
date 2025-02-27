
import paypalrestsdk
from django.conf import settings
from django.shortcuts import render, redirect
from shopping_cart_app.models import Cart
from .models import Payment
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse







# Configure PayPal
paypalrestsdk.configure({
    "mode": settings.PAYPAL_MODE,
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET
})

@login_required(login_url="user_login")
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

@login_required(login_url="user_login")
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



@login_required(login_url="user_login")
def payment_cancel(request):
    return render(request, "payment_cancel.html")







@login_required(login_url="user_login")
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





@login_required(login_url="user_login")
def bill_receipt(request, payment_id):
    payment = Payment.objects.get( paypal_payment_id=payment_id)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="receipt_{payment_id}.pdf"'

    # Create PDF
    pdf = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(200, height - 50, "Payment Receipt")

    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, height - 100, f"Payment ID: {payment.paypal_payment_id}")
    pdf.drawString(50, height - 120, f"Sale ID: {payment.paypal_sale_id if payment.paypal_sale_id else 'N/A'}")
    pdf.drawString(50, height - 140, f"User: {payment.user.username}")
    pdf.drawString(50, height - 160, f"Amount Paid: ${payment.amount}")
    pdf.drawString(50, height - 180, f"Status: {payment.status}")
    pdf.drawString(50, height - 200, f"Date: {payment.created_on.strftime('%Y-%m-%d %H:%M:%S')}")

    pdf.line(50, height - 220, 550, height - 220)  # Line separator

    pdf.drawString(50, height - 250, "Products Purchased:")

    y = height - 270
    for product in payment.product.all():
        pdf.drawString(50, y, f"- {product.name}  (${product.price}) ")
        y -= 20

    pdf.drawString(50, y - 30, "Thank you for your purchase!")

    pdf.showPage()
    pdf.save()

    return response
