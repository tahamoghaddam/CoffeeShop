from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, CustomAuthenticationForm, ProductForm, ProductIngredientFormSet, IngredientForm, UpdateIngredientForm,DeliveryMethodForm
from .models import Ingredient, Product, Cart, CartItem, Orders, Orders_Product
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Count, Sum
from datetime import datetime, timedelta

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
    
    # Categories
    categories = {
        'hot': 'Hot Drinks',
        'cold': 'Cold Drinks',
        'cakes': 'Cakes & Desserts',
        'breakfasts': 'Breakfast'
    }
    products = Product.objects.all()

    context = {
        'popular_products': popular_products_details,
        'categories': categories.items(),
        'products': products,
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
            return redirect('product_list')  # Replace 'success_url' with your desired redirect

    else:
        product_form = ProductForm()
        formset = ProductIngredientFormSet()

    return render(request, 'addproduct.html', {'product_form': product_form, 'formset': formset})

######################################################################################

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('cart_detail')

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
    return render(request, 'shoppingcart.html', {'cart': cart, 'form': form})

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    return redirect('cart_detail')

@login_required
def order_success(request):
    return render(request, 'cart/order_success.html')

######################################################################################

@login_required
def shopping_history(request):
    orders = Orders.objects.filter(username=request.user).order_by('-date')
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

def order_monitor(request):
    return render(request, 'order_monitor.html')

def get_orders_data(request):
    filter_type = request.GET.get('filter', 'daily')
    today = datetime.today()
    
    if filter_type == 'daily':
        start_date = today - timedelta(days=1)
    elif filter_type == 'weekly':
        start_date = today - timedelta(weeks=1)
    elif filter_type == 'monthly':
        start_date = today - timedelta(days=30)
    else:
        start_date = today - timedelta(days=1)

    orders = Orders_Product.objects.filter(order_id__timestamp__gte=start_date).values('product_id__name').annotate(total_quantity=Sum('quantity'))

    data = {
        'labels': [order['product_id__name'] for order in orders],
        'data': [order['total_quantity'] for order in orders],
    }

    return JsonResponse(data)

######################################################################################

def menu_view(request):
    return render(request, 'product.html')