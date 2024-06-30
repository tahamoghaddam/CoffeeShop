from django import forms
from django.core.exceptions import ValidationError
from .models import Category, Ingredient, Product, ProductIngredient, Orders, Orders_Product
from django.db.models import F
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=15, required=False)

    class Meta:
        model = get_user_model()
        fields = ('username', 'email', 'phone_number', 'password1', 'password2')

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label='Email or Username')



class IngredientForm(forms.ModelForm):
    class Meta:
        model = Ingredient
        fields = ['name', 'quantity']

class UpdateIngredientForm(forms.Form):
    name = forms.CharField(max_length=100)
    new_quantity = forms.FloatField()

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'description', 'image', 'category']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(name__in=['cold', 'hot', 'cakes', 'desserts'])

class ProductIngredientForm(forms.ModelForm):
    class Meta:
        model = ProductIngredient
        fields = ['ingredient', 'quantity']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ingredient'].queryset = Ingredient.objects.filter(name__in=['flour', 'sugar', 'milk', 'coffee'])

ProductIngredientFormSet = forms.inlineformset_factory(Product, ProductIngredient, form=ProductIngredientForm, extra=1)

class OrdersForm(forms.ModelForm):
    class Meta:
        model = Orders
        fields = ['username', 'type', 'date', 'open']

class OrdersProductForm(forms.ModelForm):
    class Meta:
        model = Orders_Product
        fields = ['quantity', 'product_id', 'order_id']

    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get('product_id')
        quantity = cleaned_data.get('quantity')

        if product and quantity:
            product_ingredients = ProductIngredient.objects.filter(product=product)
            for product_ingredient in product_ingredients:
                ingredient = product_ingredient.ingredient
                required_quantity = product_ingredient.quantity * quantity
                if ingredient.quantity < required_quantity:
                    raise ValidationError(f"Not enough {ingredient.name} to fulfill the order.")

        return cleaned_data

    def save(self, commit=True):
        order_product = super().save(commit=False)
        product = order_product.product_id
        quantity = order_product.quantity

        if commit:
            order_product.save()
            product_ingredients = ProductIngredient.objects.filter(product=product)
            for product_ingredient in product_ingredients:
                ingredient = product_ingredient.ingredient
                required_quantity = product_ingredient.quantity * quantity
                ingredient.quantity = F('quantity') - required_quantity
                ingredient.save()

        return order_product

OrdersProductFormSet = forms.inlineformset_factory(Orders, Orders_Product, form=OrdersProductForm, extra=1)
