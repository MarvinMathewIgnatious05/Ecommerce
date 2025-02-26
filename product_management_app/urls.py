from django.urls import path
from .views import view_product, product_details, about, contact

from django.conf import settings
from django.conf.urls.static import static

app_name = "product_management_app"

urlpatterns = [
    path("view_product/", view_product, name ="viewproduct"),
    path("product_details/<int:id>", product_details, name="productdetails"),
    path("about", about, name="about"),
    path("contact", contact, name="contact"),



]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)