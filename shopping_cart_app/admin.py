from django.contrib import admin
from .models import Cart
# Register your models here.
# admin.site.register(Cart)

class CartAdmin(admin.ModelAdmin):
    list_display = ("product_id", "quantity", "user")
admin.site.register(Cart, CartAdmin)