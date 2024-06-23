from django.db import models
from django.core.exceptions import ValidationError

class Ingredient(models.Model):
    name = models.CharField(max_length=100)
    quantity = models.FloatField()

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    category = models.CharField(max_length=100)
    ingredients = models.ManyToManyField(Ingredient, through='ProductIngredient')

    def __str__(self):
        return self.name

class ProductIngredient(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.FloatField()

    def __str__(self):
        return f"{self.quantity} of {self.ingredient.name} for {self.product.name}"


class Order(models.Model):
    DELIVERY_CHOICES = [
        ('standard', 'Standard Delivery'),
        ('express', 'Express Delivery'),
    ]

    products = models.ManyToManyField(Product)
    delivery_method = models.CharField(max_length=10, choices=DELIVERY_CHOICES)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Order {self.id} - {self.delivery_method}"