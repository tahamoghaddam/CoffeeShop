from django import forms
from .models import Product, Ingredient
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import Product, ProductIngredient, Ingredient
from .models import CartItem


class SignUpForm(UserCreationForm):
    # Custom fields
    email = forms.EmailField()
    name = forms.CharField()

    class Meta:
        model = User
        fields = ["name", "username", "email", "password"]


class LoginForm(forms.Form):
    username_or_email = forms.CharField(max_length=63)
    password = forms.CharField(max_length=63, widget=forms.PasswordInput)

# new product form
from django import forms
from .models import Ingredient

class IngredientForm(forms.ModelForm):
    class Meta:
        model = Ingredient
        fields = ['name', 'quantity']


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'description', 'image', 'category']

class ProductIngredientForm(forms.ModelForm):
    class Meta:
        model = ProductIngredient
        fields = ['ingredient', 'quantity']

ProductIngredientFormSet = forms.inlineformset_factory(Product, ProductIngredient, form=ProductIngredientForm, extra=1)

from django import forms
from .models import CartItem

class CartItemForm(forms.ModelForm):
    class Meta:
        model = CartItem
        fields = ['product', 'quantity']
