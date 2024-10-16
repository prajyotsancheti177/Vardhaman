from django.db import models

# Create your models here.
class PriceCalculation(models.Model):
    product_name = models.CharField(max_length=255)
    product_price = models.FloatField(default=0)