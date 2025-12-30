from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core import validators
from django.db.models import F
from django.conf import settings

class Storage(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True, null=False, blank=False)
    amount = models.PositiveIntegerField(null=False, blank=False, validators=[validators.MinValueValidator(0, "error")])

class Ingredient(models.Model):
    name = models.CharField(max_length=100, unique=True, null=False, blank=False, primary_key=True)
    quantity = models.FloatField()

    def __str__(self):
        return self.name

class Product(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True, null=False, blank=False)
    price = models.PositiveIntegerField(null=False, blank=False)
    description = models.TextField()
    image = models.ImageField(upload_to='products', null=False, blank=False, default=None)
    category = models.CharField(max_length=50, choices=[
        ('hot', 'Hot Drinks'),
        ('cold', 'Cold Drinks'),
        ('cakes', 'Cakes'),
        ('breakfasts', 'Breakfasts')
    ])
    ingredients = models.ManyToManyField(Ingredient, through='ProductIngredient')

    def __str__(self):
        return self.name

    def check_availability(self, quantity):
        for pi in self.productingredient_set.all():
            if pi.ingredient.quantity < (pi.quantity * quantity):
                return False
        return True

class ProductIngredient(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.FloatField()

class Order(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders', null=True)
    is_takeout = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_open = models.BooleanField(default=True)

    @property
    def total_price(self):
        return sum(item.subtotal for item in self.items.all())
    
    class Meta:
        verbose_name_plural = "Orders"

class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    @property
    def subtotal(self):
        return self.product.price * self.quantity

    def save(self, *args, **kwargs):
        # Deduct ingredients ONLY when the order item is first created
        if not self.pk:
            self.reduce_ingredients()
        super().save(*args, **kwargs)

    def reduce_ingredients(self):
        for pi in self.product.productingredient_set.all():
            Ingredient.objects.filter(name=pi.ingredient.name).update(
                quantity=F('quantity') - (pi.quantity * self.quantity)
            )

class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    # Simplified CartItem: Do NOT reserve stock. Check availability on 'add' and 'checkout'.
    # This avoids complex reserve/release logic.