from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core import validators
from django.db.models import F
from django.contrib.auth.models import AbstractUser
from django.db import models


class Storage(models.Model):
    id = models.AutoField(primary_key= True)
    name = models.CharField(max_length=255 , unique= True , null= False , blank= False)
    amount = models.PositiveIntegerField(null= False , blank= False , validators= [validators.MinValueValidator(0,"error")])

class Category(models.Model):
    CATEGORY_CHOICES = [
        ('cold', 'Cold'),
        ('hot', 'Hot'),
        ('cakes', 'Cakes'),
        ('desserts', 'Desserts'),
    ]
    name = models.CharField(max_length=50, choices=CATEGORY_CHOICES)

class Ingredient(models.Model):
    name = models.CharField(max_length=100)
    quantity = models.FloatField()

class Product(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True, null=False, blank=False)
    price = models.PositiveIntegerField(null=False, blank=False)
    description = models.TextField()
    image = models.ImageField(upload_to='products/', null=False, blank=False, default=None)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    ingredients = models.ManyToManyField(Ingredient, through='ProductIngredient')

class ProductIngredient(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.FloatField()

class Orders(models.Model):
    order_id = models.AutoField(primary_key=True, unique=True)
    username = models.CharField(max_length=255)
    type = models.BooleanField(default=True)  # is 1 if the order is take out and 0 if not.
    date = models.DateField(auto_created=True, default=timezone.now)
    open = models.BooleanField(default=True)

    def Overall_Price(self):
        total_price = sum(item.product_id.price * item.quantity for item in self.orders_product_set.all())
        return total_price

class Orders_Product(models.Model):
    id = models.AutoField(primary_key=True)
    quantity = models.IntegerField()
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    order_id = models.ForeignKey(Orders, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if not self.can_fulfill_order():
            raise ValidationError("Not enough ingredients to fulfill the order.")
        super().save(*args, **kwargs)
        self.reduce_ingredient_quantity()

    def can_fulfill_order(self):
        product_ingredients = ProductIngredient.objects.filter(product=self.product_id)
        for product_ingredient in product_ingredients:
            ingredient = product_ingredient.ingredient
            required_quantity = product_ingredient.quantity * self.quantity
            if ingredient.quantity < required_quantity:
                return False
        return True

    def reduce_ingredient_quantity(self):
        product_ingredients = ProductIngredient.objects.filter(product=self.product_id)
        for product_ingredient in product_ingredients:
            ingredient = product_ingredient.ingredient
            required_quantity = product_ingredient.quantity * self.quantity
            ingredient.quantity = F('quantity') - required_quantity
            ingredient.save()

        # Refresh the ingredient from the database to get the latest quantity
        for product_ingredient in product_ingredients:
            product_ingredient.ingredient.refresh_from_db()

