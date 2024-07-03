from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from .forms import CustomUserCreationForm, CustomAuthenticationForm, ProductForm, ProductIngredientFormSet, IngredientForm, UpdateIngredientForm,DeliveryMethodForm
from .models import Ingredient, Product, Cart, CartItem, Orders, Orders_Product
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Count, Sum
from datetime import datetime, timedelta
import json
from django.contrib import messages

######################################################################################

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)  # Use auth_login to avoid conflict
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})

def user_login(request):  # Rename the function to avoid conflict
    if request.method == 'POST':
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)  # Use auth_login to avoid conflict
            if user.is_staff:
                return redirect('admin_page')
            else:
                return redirect('home')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'login.html', {'form': form})

######################################################################################

@login_required
def home(request):
    # Annotate Orders_Product to get the total quantity ordered for each product
    popular_products = Orders_Product.objects.values('product_id').annotate(total_quantity=Sum('quantity')).order_by('-total_quantity')[:5]
    
    # Fetch the actual product details for the popular products
    popular_products_details = []
    for item in popular_products:
        try:
            product = Product.objects.get(id=item['product_id'])
            popular_products_details.append({
                'product': product,
                'total_quantity': item['total_quantity']
            })
        except Product.DoesNotExist:
            continue
    
    context = {
        'popular_products': popular_products_details,
    }
    return render(request, 'home.html', context)



@login_required
def admin_view(request):
    return render(request, 'admin_page.html')

######################################################################################

@login_required
def add_product(request):
    if request.method == "POST":
        product_form = ProductForm(request.POST, request.FILES)
        formset = ProductIngredientFormSet(request.POST)

        if product_form.is_valid() and formset.is_valid():
            product = product_form.save()
            formset.instance = product
            formset.save()
            return redirect('product')  # Replace 'success_url' with your desired redirect

    else:
        product_form = ProductForm()
        formset = ProductIngredientFormSet()

    return render(request, 'addproduct.html', {'product_form': product_form, 'formset': formset})

######################################################################################

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity'))
        
        # Check ingredient availability
        if not CartItem.check_ingredient_availability(product, quantity):
            messages.error(request, 'Not enough ingredients to add this item to your cart.')
            return redirect('product')  # Or redirect to the same product page
        
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        
        if not created:
            # Update existing item quantity and check ingredient availability again
            new_quantity = cart_item.quantity + quantity
            if not CartItem.check_ingredient_availability(product, new_quantity):
                messages.error(request, 'Not enough ingredients to increase the quantity of this item.')
                return redirect('shoppingcart')
            cart_item.quantity = new_quantity
        else:
            cart_item.quantity = quantity
        
        cart_item.save()
        return redirect('shoppingcart')

    return redirect('product')

@login_required
def cart_detail(request):
    cart = get_object_or_404(Cart, user=request.user)
    if request.method == 'POST':
        form = DeliveryMethodForm(request.POST)
        if form.is_valid():
            delivery_method = form.cleaned_data['delivery_method']
            order = Orders.objects.create(
                username=request.user.username,
                type=delivery_method,
                date=timezone.now(),
                open=True,
            )
            for item in cart.items.all():
                Orders_Product.objects.create(
                    order_id=order,
                    product_id=item.product,
                    quantity=item.quantity
                )
            cart.items.all().delete()
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
        'cart_items': cart_items,
        'cart_total': cart_total,
        'form': form
    })


@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    return redirect('cart_detail')

@login_required
def order_success(request):
    return render(request, 'order_success.html')

######################################################################################

@login_required
def shopping_history(request):
    orders = Orders.objects.filter(username=request.user).order_by('-date')

    orders_with_totals = []
    for order in orders:
        order_total = 0
        items_with_totals = []
        for item in order.orders_product_set.all():
            item_total = item.product.price * item.quantity
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
    return render(request, 'shopping-history.html', {'orders': orders})

######################################################################################

def inventory_view(request):
    ingredients = Ingredient.objects.all()
    return render(request, 'inventory.html', {'ingredients': ingredients})

def add_ingredient(request):
    if request.method == 'POST':
        form = IngredientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('success')
    else:
        form = IngredientForm()
    return render(request, 'add_ingredient.html', {'form': form})

def update_ingredient(request, name):
    try:
        ingredient = Ingredient.objects.get(name=name)
    except Ingredient.DoesNotExist:
        return redirect('inventory_view')

    if request.method == 'POST':
        form = UpdateIngredientForm(request.POST)
        if form.is_valid():
            new_quantity = form.cleaned_data['new_quantity']
            ingredient.quantity = new_quantity
            ingredient.save()
            return redirect('success')
    else:
        form = UpdateIngredientForm(initial={'name': ingredient.name, 'new_quantity': ingredient.quantity})
    return render(request, 'update_ingredient.html', {'form': form, 'ingredient': ingredient})

def ingredient_success(request):
    return render(request, 'success.html')


######################################################################################

def monitor_orders(request):
    # Process GET parameters for filtering
    product_id = request.GET.get('product_id')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Initialize filter parameters
    filters = {}
    if product_id:
        filters['product_id_id'] = product_id
    if start_date:
        filters['order_id__date__gte'] = start_date
    if end_date:
        filters['order_id__date__lte'] = end_date

    # Filter and aggregate orders
    order_products = Orders_Product.objects.filter(**filters)
    order_data = order_products.values('product_id__name').annotate(total_quantity=Sum('quantity'))

    # Prepare data for Chart.js
    labels = [entry['product_id__name'] for entry in order_data]
    data = [entry['total_quantity'] for entry in order_data]

    context = {
        'products': Product.objects.all(),
        'labels': json.dumps(labels),
        'data': json.dumps(data)
    }
    return render(request, 'monitor_orders.html', context)

######################################################################################

def menu_view(request):
    pp=Product.objects.all()
    context = {'products':pp}
    return render(request, 'product.html',context)