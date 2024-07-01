from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, CustomAuthenticationForm, ProductForm, ProductIngredientFormSet, IngredientForm, UpdateIngredientForm,DeliveryMethodForm
from .models import Ingredient, Product, Cart, CartItem, Orders, Orders_Product
from django.http import JsonResponse
from django.utils import timezone

######################################################################################

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})


def login(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if user.is_staff:
                return redirect('admin_page')
            else:
                return redirect('home')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'login.html', {'form': form})

######################################################################################

def home(request):
    #popular_products = get_popular_products()
    #context = {'popular_products': popular_products}
    return render(request, 'home.html')


def admin_view(request):
    return render(request, 'admin_page.html')

######################################################################################

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


#def get_popular_products():
#    popular_products = (OrderItem.objects.values('product__id', 'product__name', 'product__price', 'product__image')
#                        .annotate(total_quantity=sum('quantity'))
#                        .order_by('-total_quantity')[:5])
#    return popular_products

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