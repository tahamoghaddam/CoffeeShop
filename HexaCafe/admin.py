from django.contrib import admin
from .models import Product, Ingredient, ProductIngredient, Orders, Storage

admin.site.register(Product)
admin.site.register(Ingredient)
admin.site.register(ProductIngredient)
admin.site.register(Orders)
admin.site.register(Storage)