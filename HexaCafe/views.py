from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from .forms import ProductForm
from .forms import SignUpForm
from .forms import LoginForm
from .models import Product, Order
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.contrib.auth.decorators import login_required
from .forms import ProductForm, ProductIngredientFormSet, ProductIngredientForm
from .models import Product, Ingredient
from django.http import JsonResponse
import json
from .models import Cart, CartItem, Order, OrderItem, Product
from .forms import CartItemForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Ingredient
from .forms import IngredientForm



def home(request):
     context = {}
     return render(request, 'home.html',context)

def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login/')
        else:
            errors = form.errors.as_json()
            return JsonResponse({"error": errors}, status=400)
    else:
        form = SignUpForm()
    return render(request, "signup.html", {"form": form})



def login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username_or_email = form.cleaned_data["username_or_email"]
            password = form.cleaned_data["password"]

            # Check if the input is a valid username or email
            user = authenticate(request, username=username_or_email, password=password)
            if user:
                if user.is_staff:  # Admin
                    # Redirect to management panel
                    return redirect("admin:index")
                else:
                    # Redirect to home page
                    return redirect("home.html")
    else:
        form = LoginForm()
    return render(request, "login.html", {"form": form})


@login_required
def add_product(request):
    if request.method == 'POST':
        product_form = ProductForm(request.POST, request.FILES)
        formset = ProductIngredientFormSet(request.POST)
        if product_form.is_valid() and formset.is_valid():
            product = product_form.save()
            formset.instance = product
            formset.save()
            return redirect('product_list')  # Adjust to your URL
    else:
        product_form = ProductForm()
        formset = ProductIngredientFormSet()

    return render(request, 'addproduct.html', {'product_form': product_form, 'formset': formset})


def process_order(product_id, quantity_ordered):
    product = Product.objects.get(id=product_id)
    for product_ingredient in product.productingredient_set.all():
        ingredient = product_ingredient.ingredient
        ingredient.quantity -= product_ingredient.quantity * quantity_ordered
        ingredient.save()

def get_popular_products():
    return Order.objects.values('product__name').annotate(total_quantity=sum('quantity')).order_by('-total_quantity')


@login_required
def cart_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)
    total = sum(item.product.price * item.quantity for item in cart_items)
    return render(request, 'cart.html', {'cart_items': cart_items, 'total': total})

@login_required
def add_to_cart(request):
    if request.method == 'POST':
        form = CartItemForm(request.POST)
        if form.is_valid():
            cart, created = Cart.objects.get_or_create(user=request.user)
            cart_item = form.save(commit=False)
            cart_item.cart = cart
            cart_item.save()
            return redirect('cart')
    else:
        form = CartItemForm()
    return render(request, 'add_to_cart.html', {'form': form})

@login_required
def order_history_view(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'order_history.html', {'orders': orders})

@login_required
def checkout(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)
    if cart_items:
        order = Order.objects.create(user=request.user)
        for item in cart_items:
            OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity)
        cart_items.delete()  # Clear the cart after checkout
    return redirect('order_history')



@login_required
def inventory_view(request):
    ingredients = Ingredient.objects.all()
    return render(request, 'inventory.html', {'ingredients': ingredients})

@login_required
def update_inventory(request, ingredient_id):
    ingredient = get_object_or_404(Ingredient, id=ingredient_id)
    if request.method == 'POST':
        form = IngredientForm(request.POST, instance=ingredient)
        if form.is_valid():
            form.save()
            return redirect('inventory')
    else:
        form = IngredientForm(instance=ingredient)
    return render(request, 'update_inventory.html', {'form': form, 'ingredient': ingredient})
