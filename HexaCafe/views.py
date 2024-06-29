from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from .forms import ProductForm
from .forms import SignUpForm
from .forms import LoginForm
from .models import Product, Order
from django.http import HttpResponse
from django.db import transaction
from .forms import ProductForm, ProductIngredientFormSet, ProductIngredientForm
from .models import Product, Ingredient
from django.http import JsonResponse
import json
from .models import Cart, CartItem, Order, OrderItem, Product
from .forms import CartItemForm
from .models import Ingredient
from .forms import IngredientForm



def home(request):
    #popular_products = get_popular_products()
    #context = {'popular_products': popular_products}
    return render(request, 'home.html')


def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login.html')  # Correct the redirect to the named URL
        else:
            errors = form.errors.as_json()
            return JsonResponse({"error": errors}, status=400)
    else:
        form = SignUpForm()
    return render(request, "signup.html", {"form": form})

def login(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username_or_email = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")

            # Check if the input is an email or username
            if '@' in username_or_email:
                try:
                    user = user.objects.get(email=username_or_email)
                    username = user.username
                except user.DoesNotExist:
                    username = None
            else:
                username = username_or_email

            user = authenticate(request, username=username, password=password)
            if user:
                user = authenticate(request, username=user.username, password=password)
                if user is not None:
                    auth_login(request, user)
                    if user.is_staff:
                        return redirect('admin_page')  # Assuming you have a URL named 'admin_page'
                    else:
                        return redirect('home.html')
            else:
                return render(request, "login.html", {"form": form, "error": "Invalid username or password"})
        else:
            return render(request, "login.html", {"form": form, "error": "Invalid username or password"})
    else:
        form = AuthenticationForm()
    return render(request, "login.html", {"form": form})




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

#def get_popular_products():
#    popular_products = (OrderItem.objects.values('product__id', 'product__name', 'product__price', 'product__image')
#                        .annotate(total_quantity=sum('quantity'))
#                        .order_by('-total_quantity')[:5])
#    return popular_products

def get_cart(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        cart = None
    return cart


@login_required(login_url='login')  # Redirect to login page if not authenticated
def cart_view(request):
    cart = get_cart(request)
    if cart:
        cart_items = CartItem.objects.filter(cart=cart)
        total = sum(item.product.price * item.quantity for item in cart_items)
        return render(request, 'shoppingcart.html', {'cart_items': cart_items, 'total': total})
    else:
        return render(request, 'shoppingcart.html', {'cart_items': [], 'total': 0})
    


@login_required(login_url='login')  # Redirect to login page if not authenticated
def add_to_cart(request):
    if request.method == 'POST':
        form = CartItemForm(request.POST)
        if form.is_valid():
            cart = get_cart(request)
            if cart:
                cart_item = form.save(commit=False)
                cart_item.cart = cart
                cart_item.save()
                return redirect('cart')
    else:
        form = CartItemForm()
    return render(request, 'add_to_cart.html', {'form': form})



def order_history_view(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'order_history.html', {'orders': orders})


def checkout(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)
    if cart_items:
        order = Order.objects.create(user=request.user)
        for item in cart_items:
            OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity)
        cart_items.delete()  # Clear the cart after checkout
    return redirect('order_history')



def inventory_view(request):
    ingredients = Ingredient.objects.all()
    return render(request, 'inventory.html', {'ingredients': ingredients})


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
