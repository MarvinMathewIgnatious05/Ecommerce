from django.db import models
from product_management_app.models import Product
from user_authentication_app.models import CustomUser
from django.contrib.auth.models import User
from django.conf import settings
# Create your models here.


class Cart(models.Model):

    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def total_price(self):
        return self.quantity * self.product.price

