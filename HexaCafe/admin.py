from django.contrib import admin
from .models import Product, Ingredient, Category, ProductIngredient, Order

admin.site.register(Product)
admin.site.register(Ingredient)
admin.site.register(Category)
admin.site.register(ProductIngredient)
admin.site.register(Order)