from django.shortcuts import render, redirect
from shopping_cart_app.models import Cart
from product_management_app.models import Product
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from django.views.decorators.cache import cache_page
from user_authentication_app.models import CustomUser
from django.contrib import messages
from django.shortcuts import HttpResponse


# def create_cart(request, id):
#     product = Product.objects.get(id=id)
#     quantity =1
#     Cart.objects.create(product_id=product, user=request.user,qunatity=quantity).value()
#     return redirect("shopping_cart_app:list_cart")




@login_required(login_url="user_login")

def create_cart(request, id):
    print(request.user, ": user")

    product = Product.objects.get(id=id)


    cart_item = Cart.objects.filter(product_id=product, user=request.user).first()

    if cart_item:
        cart_item.quantity += 1
        cart_item.save()
    else:
        Cart.objects.create(product_id=product, user=request.user, quantity=1)

    return redirect("shopping_cart_app:list_cart")





@login_required(login_url="user_login")
def list_cart(request):
    total_item = 0
    cart_products = Cart.objects.filter(user=request.user).all()
    # print(cart_products)
    total_price = sum(item.product_id.price * item.quantity for item in cart_products)

    for item in cart_products:
        total_item+=item.quantity
        # print(total_item,"jjjjjjjj")

    return render(request, "cart.html", {"products": cart_products, "total_price":total_price, "total_item":total_item})







def remove_cart(request, id):
    cart_product = Cart.objects.get(id=id)
    if cart_product.quantity > 1:
        cart_product.quantity -= 1  # Decrease quantity by one
        # print(cart_product.product_id.price,"??????????????????????????????????????????")
        cart_product.save()
    else:
        cart_product.delete()  # If quantity reaches zero, remove from cart
    return redirect("shopping_cart_app:list_cart")


#increasing the quantity
def update_cart(request,id):
    cart_product = Cart.objects.get(id=id)
    if cart_product.quantity >0:
        cart_product.quantity +=1
        cart_product.save()
    else:
        pass
    return redirect("shopping_cart_app:list_cart")




# def update_cart(request, id):
#     if request.method == "POST":
#         quantity = int(request.POST.get("quantity", 1))
#
#         cart_item, created = Cart.objects.get_or_create(id=id, defaults={"quantity": quantity})
#
#         if not created:
#             cart_item.quantity = quantity
#             cart_item.save()
#
#         return redirect("shopping_cart_app:list_cart")



def delete_cart(request):

    cart_product = Cart.objects.filter(user=request.user).all()
    cart_product.delete()
    return redirect("shopping_cart_app:list_cart")


def single_cart_checkout(request,id):
    cart_product = Cart.objects.get(id=id)
    total_price = cart_product.product_id.price * cart_product.quantity
    print(total_price,"calculated sssssssssssssssssssssss")

    return render(request,"checkout.html",{"total_price":total_price,"cart_item": cart_product})


@login_required(login_url="user_login")
def checkout(request):
    # return HttpResponse("NETWORK ERROR PLZ wait")

    cart_products = Cart.objects.filter(user=request.user).all()
    print(cart_products)
    total_price = sum(item.product_id.price * item.quantity for item in cart_products)


    return render(request, "checkout.html",{"total_price":total_price})






