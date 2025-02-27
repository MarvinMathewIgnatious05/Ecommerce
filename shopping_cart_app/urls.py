from django.urls import path
from shopping_cart_app.views import create_cart, list_cart, remove_cart, update_cart, delete_cart, single_cart_checkout, checkout
from django.conf import settings
from django.conf.urls.static import static

app_name = "shopping_cart_app"
urlpatterns = [

    path('add/<int:id>', create_cart, name='create_cart'),
    path('cart/', list_cart, name='list_cart'),
    path('remove/<int:id>',remove_cart, name='remove_cart'),
    path('update/<int:id>',update_cart, name='update_cart'),
    path('delete', delete_cart, name='delete_cart'),
    path('single/<int:id>', single_cart_checkout, name='single_cart_checkout'),
    path('checkout/', checkout, name="checkout"),



]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
