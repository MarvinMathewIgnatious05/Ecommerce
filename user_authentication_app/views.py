from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model


# Create your views here.


# @login_required(login_url="user_login")
def user_registration(request):
    User = get_user_model()


    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone_number')
        address = request.POST.get('address')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        profile_picture = request.FILES.get('profile_picture')

        if password == confirm_password:
            user = User.objects.create_user(username=username, first_name=first_name, email=email, phone_number=phone,
                                            address=address, password=password, profile_picture=profile_picture)
            user.save()
            return redirect("user_login")


        else:
            messages.error(request, "password not match")

    return render(request, "user_registration.html")


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        # login(request, user)
        # login_required(request,user)

        if user:
            login(request, user)

            messages.success(request, " successfully login")
            return redirect("view_product/")

        else:
            messages.error(request, "invalid username or password")
            print("invalid username or password")

    return render(request, "user_login.html")


@login_required(login_url="user_login")
def logout_user(request):
    logout(request)


@login_required(login_url="user_login")
def user_profile_view(request):
    user = request.user
    # print("user:", user)
    return render(request, "user_view.html", {"user_view": user})


@login_required(login_url="user_login")
def user_profile_edit(request):
    user = request.user
    if request.method == 'POST':
        user_name = request.POST.get("username")
        f_name = request.POST.get("first_name")
        email = request.POST.get("email")
        phone = request.POST.get("phone_number")
        address = request.POST.get("address")
        profile_picture = request.FILES.get("profile_picture")

        user.username = user_name
        user.first_name = f_name
        user.email = email
        user.phone_number = phone
        user.address = address

        if profile_picture:
            user.profile_picture = profile_picture

        else:
            pass

        user.save()
        return redirect("user_view")

    return render(request, "user_edit.html", {"user_edit": user})
