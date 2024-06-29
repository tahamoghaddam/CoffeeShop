from django import forms
from .models import Product, Ingredient
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Product, ProductIngredient, Ingredient
from .models import CartItem, Category


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    name = forms.CharField(max_length=150)

    class Meta:
        model = User
        fields = ["name", "username", "email", "password1", "password2"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["name"]
        if commit:
            user.save()
        return user

class LoginForm(forms.Form):
    username_or_email = forms.CharField(max_length=63)
    password = forms.CharField(max_length=63, widget=forms.PasswordInput)


# new product form


class IngredientForm(forms.ModelForm):
    class Meta:
        model = Ingredient
        fields = ['name', 'quantity']


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


class CartItemForm(forms.ModelForm):
    class Meta:
        model = CartItem
        fields = ['product', 'quantity']