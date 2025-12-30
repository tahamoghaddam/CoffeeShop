import json
from datetime import datetime, timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db import transaction
from django.db.models import Sum, Count
from django.utils import timezone
from django.http import JsonResponse

from .forms import (
    CustomUserCreationForm, CustomAuthenticationForm, ProductForm, 
    ProductIngredientFormSet, IngredientForm, UpdateIngredientForm, DeliveryMethodForm
)
from .models import Ingredient, Product, Cart, CartItem, Order, OrderProduct

# --- Helpers ---

def admin_required(user):
    return user.is_superuser

# --- Authentication ---

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            messages.success(request, "Account created successfully!")
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            if user.is_staff or user.is_superuser:
                return redirect('admin_page')
            else:
                return redirect('home')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'login.html', {'form': form})

# --- Storefront ---

@login_required
def home(request):
    """
    Renders the home page with the top 5 popular products.
    """
    popular_products = (
        OrderProduct.objects.values('product', 'product__name', 'product__price', 'product__image')
        .annotate(total_quantity=Sum('quantity'))
        .order_by('-total_quantity')[:5]
    )
    
    popular_products_details = []
    for item in popular_products:
        try:
            p = Product.objects.get(id=item['product'])
            popular_products_details.append({
                'product': p,
                'total_quantity': item['total_quantity']
            })
        except Product.DoesNotExist:
            continue

    return render(request, 'home.html', {'popular_products': popular_products_details})

@login_required
def menu_view(request):
    products = Product.objects.all()
    return render(request, 'product.html', {'products': products})

# --- Cart Logic ---

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, _ = Cart.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        
        # Check availability before adding to cart
        if not product.check_availability(quantity):
            messages.error(request, f"Sorry, we do not have enough ingredients for {quantity}x {product.name}.")
            return redirect('product') # Redirect to menu/product page

        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        
        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
        
        cart_item.save()
        messages.success(request, f"Added {quantity} x {product.name} to cart.")
        return redirect('shoppingcart')

    return redirect('shoppingcart')

@login_required
def cart_detail(request):
    cart = get_object_or_404(Cart, user=request.user)
    if request.method == 'POST':
        form = DeliveryMethodForm(request.POST)
        if form.is_valid():
            delivery_method = form.cleaned_data['delivery_method']
            
            with transaction.atomic():
                # 1. Create Order
                order = Order.objects.create(
                    user=request.user,
                    is_takeout=delivery_method, # Assuming delivery_method maps to boolean or handled by choices
                    # Note: delivery_method in form isChoiceField with True/False.
                )
                
                # 2. Create OrderProducts (Deduction happens in OrderProduct.save)
                for item in cart.items.all():
                    # Check availability again just in case (optional but good)
                    if not item.product.check_availability(item.quantity):
                         messages.error(request, f"Ingredients run out for {item.product.name} during checkout.")
                         raise ValidationError("Stock changed during checkout") # Rollback

                    OrderProduct.objects.create(
                        order=order,
                        product=item.product,
                        quantity=item.quantity
                    )
                
                # 3. Clear Cart
                cart.items.all().delete()
                
            messages.success(request, "Order placed successfully!")
            return redirect('order_success')
    else:
        form = DeliveryMethodForm()

    cart_items = []
    cart_total = 0
    for item in cart.items.all():
        item_total = item.product.price * item.quantity
        cart_total += item_total
        cart_items.append({
            'product': item.product,
            'quantity': item.quantity,
            'item_total': item_total,
            'id': item.id
        })
    
    return render(request, 'shoppingcart.html', {
        'cart': cart, 
        'form': form, 
        'cart_items': cart_items, 
        'cart_total': cart_total
    })

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    return redirect('shoppingcart') # Ensure consistent redirect name

@login_required
def order_success(request):
    return render(request, 'order_success.html')

# --- Shopping History ---

@login_required
def shopping_history(request):
    # Filter by user object
    orders = Order.objects.filter(user=request.user).order_by('-timestamp')

    orders_with_totals = []
    for order in orders:
        order_total = 0
        items_with_totals = []
        # Access items via related_name='items' from Order model
        for item in order.items.all():
            item_total = item.subtotal
            order_total += item_total
            items_with_totals.append({
                'product': item.product,
                'quantity': item.quantity,
                'item_total': item_total,
            })
        orders_with_totals.append({
            'order': order,
            'items': items_with_totals,
            'order_total': order_total,
        })
    return render(request, 'shopping-history.html', {'orders_with_totals': orders_with_totals})

# --- Admin & Inventory ---

@user_passes_test(admin_required)
def admin_view(request):
    return render(request, 'admin_page.html')

@user_passes_test(admin_required)
def inventory_view(request):
    ingredients = Ingredient.objects.all().order_by('name')
    return render(request, 'inventory.html', {'ingredients': ingredients})

@user_passes_test(admin_required)
def add_product(request):
    if request.method == "POST":
        product_form = ProductForm(request.POST, request.FILES)
        formset = ProductIngredientFormSet(request.POST)

        if product_form.is_valid() and formset.is_valid():
            product = product_form.save()
            formset.instance = product
            formset.save()
            return redirect('product')
    else:
        product_form = ProductForm()
        formset = ProductIngredientFormSet()

    return render(request, 'addproduct.html', {'product_form': product_form, 'formset': formset})

@user_passes_test(admin_required)
def add_ingredient(request):
    if request.method == 'POST':
        form = IngredientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('success')
    else:
        form = IngredientForm()
    return render(request, 'add_ingredient.html', {'form': form})

@user_passes_test(admin_required)
def update_ingredient(request, name):
    ingredient = get_object_or_404(Ingredient, name=name)
    if request.method == 'POST':
        form = UpdateIngredientForm(request.POST)
        if form.is_valid():
            ingredient.quantity = form.cleaned_data['new_quantity']
            ingredient.save()
            return redirect('success')
    else:
        form = UpdateIngredientForm(initial={'name': ingredient.name, 'new_quantity': ingredient.quantity})
    return render(request, 'update_ingredient.html', {'form': form, 'ingredient': ingredient})

@user_passes_test(admin_required)
def ingredient_success(request):
    return render(request, 'success.html')

@user_passes_test(admin_required)
def monitor_orders(request):
    """
    Admin view to monitor completed orders with filtering options.
    """
    product_id = request.GET.get('product_id')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    filters = {'order__is_open': False}
    
    if product_id:
        filters['product_id'] = product_id
    if start_date:
        filters['order__timestamp__gte'] = start_date
    if end_date:
        filters['order__timestamp__lte'] = end_date
    
    order_data = (
        OrderProduct.objects.filter(**filters)
        .values('product__name')
        .annotate(total_quantity=Sum('quantity'))
    )

    labels = [entry['product__name'] for entry in order_data]
    data = [entry['total_quantity'] for entry in order_data]

    context = {
        'products': Product.objects.all(),
        'labels': json.dumps(labels),
        'data': json.dumps(data)
    }
    return render(request, 'monitor_orders.html', context)
