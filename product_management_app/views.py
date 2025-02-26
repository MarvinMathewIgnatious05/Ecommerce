from django.shortcuts import render
from .models import Product
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from .forms import NameForm
from django.shortcuts import HttpResponse
# Create your views here.



@login_required(login_url="user_login")
def view_product(request):
   product = Product.objects.all().values()
   # print(product)
   return render(request,"view_product.html", {'product':product})




@login_required(login_url="user_login")
@never_cache
def product_details(request,id):
   product_detail = Product.objects.get(id=id)
   product_detail.save()
   return render(request,"product_details.html", {'product_detail':product_detail})




@login_required(login_url="user_login")
def about(request):
   return render(request,"about.html")

# @login_required(login_url="user_login")
# def contact(request):
#    return render(request,"contact.html")





#django forms
@login_required(login_url="user_login")
def contact(request):

   # if request.method == 'POST':
   form = NameForm()

   return render(request, "contact.html", {"form": form})