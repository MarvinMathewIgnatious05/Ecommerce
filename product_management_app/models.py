from django.db import models


# Create your models here.


class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_length=10, decimal_places=2, max_digits=10)
    stock_availability = models.PositiveIntegerField(default=0)
    tags = models.CharField(max_length=100)
    images = models.ImageField(upload_to="product_images/", blank=True, null=True)

    def __str__(self):
        return self.name
