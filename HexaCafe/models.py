from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=50)


class Ingredient(models.Model):
    name = models.CharField(max_length=100)
    quantity = models.FloatField()


class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    image = models.ImageField(upload_to='products/')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    ingredients = models.ManyToManyField(Ingredient, through='ProductIngredient')


class ProductIngredient(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.FloatField()  # Quantity of ingredient used in the product

class Order(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    order_date = models.DateField(auto_now_add=True)


class Order_cart(models.Model):
    DELIVERY_CHOICES = [
        ('standard', 'Standard Delivery'),
        ('express', 'Express Delivery'),
    ]

    products = models.ManyToManyField(Product)
    delivery_method = models.CharField(max_length=10, choices=DELIVERY_CHOICES)
    # total price 
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

