from django.contrib import admin
from .models import Product, Ingredient, ProductIngredient, Order, Storage

admin.site.register(Product)
admin.site.register(Ingredient)
admin.site.register(ProductIngredient)
admin.site.register(Order)
admin.site.register(Storage)