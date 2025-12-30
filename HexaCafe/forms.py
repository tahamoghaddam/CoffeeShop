from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Ingredient, Product, ProductIngredient, Order, OrderProduct, CartItem

# --- User Authentication ---

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=15, required=False)
    
    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ('username', 'email', 'phone_number', 'password1', 'password2')

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label='Email or Username', widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    # Default authentication form 'clean' method handles authentication, 
    # but the previous code had custom logic.
    # We'll stick to standard behavior unless custom auth is strictly required. 
    # The previous code required 'is_active', which standard does too.
    # We will keep it simple.

# --- Product & Ingredient Management (Admin) ---

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'description', 'image', 'category']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'category': forms.Select(attrs={'class': 'form-select'}),
        }

class ProductIngredientForm(forms.ModelForm):
    class Meta:
        model = ProductIngredient
        fields = ['ingredient', 'quantity']
        widgets = {
            'ingredient': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'step': '0.1', 'class': 'form-control'}),
        }

# Formset for adding ingredients while creating a product
ProductIngredientFormSet = forms.inlineformset_factory(
    Product, ProductIngredient, form=ProductIngredientForm, extra=1, can_delete=True
)

class IngredientForm(forms.ModelForm):
    class Meta:
        model = Ingredient
        fields = ['name', 'quantity']

class UpdateIngredientForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly', 'class': 'form-control-plaintext'}))
    new_quantity = forms.FloatField(label="New Stock Level", widget=forms.NumberInput(attrs={'class': 'form-control'}))

# --- Ordering & Checkout ---

class DeliveryMethodForm(forms.Form):
    DELIVERY_CHOICES = [
        (True, 'Takeout'),
        (False, 'Eat-in'),
    ]
    delivery_method = forms.ChoiceField(
        choices=DELIVERY_CHOICES, 
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        initial=True
    )

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['user', 'is_takeout', 'is_open']
        # Note: 'timestamp' is auto_now_add, not editable.

class OrderProductForm(forms.ModelForm):
    class Meta:
        model = OrderProduct
        fields = ['quantity', 'product', 'order']

    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get('product')
        quantity = cleaned_data.get('quantity')

        # Logic moved to model or view, but we can keep validation here.
        if product and quantity:
             if not product.check_availability(quantity):
                 raise ValidationError(f"Insufficient ingredients to make {quantity}x {product.name}.")
        return cleaned_data

# Formset might not be used directly in views I saw, but good to update.
OrderProductFormSet = forms.inlineformset_factory(Order, OrderProduct, form=OrderProductForm, extra=1)