from django.urls import path
from .views import user_registration, user_login, user_profile_view, user_profile_edit


# app_name = "user_authentication_app"

urlpatterns = [
    path('user_registration/', user_registration, name="user_registration"),
    path("", user_login, name="user_login"),
    path('user_view', user_profile_view, name="user_view"),
    path('user_edit', user_profile_edit, name="user_edit"),

]