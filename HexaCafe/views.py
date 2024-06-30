from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, CustomAuthenticationForm, ProductForm, ProductIngredientFormSet, IngredientForm, UpdateIngredientForm
from .models import Ingredient
from django.http import JsonResponse


def home(request):
    #popular_products = get_popular_products()
    #context = {'popular_products': popular_products}
    return render(request, 'home.html')


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
            if user.is_staff:  # Assuming staff users are admins
                return redirect('admin_page')
            else:
                return redirect('home.html')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'login.html', {'form': form})

@login_required
def home(request):
    #popular_products = get_popular_products()
    #context = {'popular_products': popular_products}
    return render(request, 'home.html')

@login_required
def admin_view(request):
    return render(request, 'admin_page.html')


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

#def get_cart(request):
#    if request.user.is_authenticated:
#        cart, created = Cart.objects.get_or_create(user=request.user)
#    else:
#        cart = None
#    return cart


#@login_required(login_url='login')  # Redirect to login page if not authenticated
#def cart_view(request):
#    cart = get_cart(request)
#    if cart:
#        cart_items = CartItem.objects.filter(cart=cart)
#        total = sum(item.product.price * item.quantity for item in cart_items)
#       return render(request, 'shoppingcart.html', {'cart_items': cart_items, 'total': total})
#   else:
#        return render(request, 'shoppingcart.html', {'cart_items': [], 'total': 0})
#    
#
#
#@login_required(login_url='login')  # Redirect to login page if not authenticated
#def add_to_cart(request):
#    if request.method == 'POST':
#        form = CartItemForm(request.POST)
#        if form.is_valid():
#            cart = get_cart(request)
#            if cart:
#                cart_item = form.save(commit=False)
#                cart_item.cart = cart
#                cart_item.save()
#                return redirect('cart')
#    else:
#        form = CartItemForm()
#    return render(request, 'add_to_cart.html', {'form': form})



#def order_history_view(request):
#    orders = Order.objects.filter(user=request.user).order_by('-created_at')
#    return render(request, 'order_history.html', {'orders': orders})


#def checkout(request):
#    cart, created = Cart.objects.get_or_create(user=request.user)
#    cart_items = CartItem.objects.filter(cart=cart)
#    if cart_items:
#        order = Order.objects.create(user=request.user)
#        for item in cart_items:
#            OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity)
#        cart_items.delete()  # Clear the cart after checkout
#    return redirect('order_history')



def inventory_view(request):
    ingredients = Ingredient.objects.all()
    return render(request, 'inventory.html', {'ingredients': ingredients})


#def update_inventory(request, ingredient_id):
#    ingredient = get_object_or_404(Ingredient, id=ingredient_id)
#    if request.method == 'POST':
#        form = IngredientForm(request.POST, instance=ingredient)
#        if form.is_valid():
#            form.save()
#            return redirect('inventory')
#    else:
#        form = IngredientForm(instance=ingredient)
#    return render(request, 'update_inventory.html', {'form': form, 'ingredient': ingredient})

def add_ingredient(request):
    if request.method == 'POST':
        form = IngredientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('ingredient_success')
    else:
        form = IngredientForm()
    return render(request, 'add_ingredient.html', {'form': form})

def update_ingredient(request):
    if request.method == 'POST':
        form = UpdateIngredientForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            new_quantity = form.cleaned_data['new_quantity']
            try:
                ingredient = Ingredient.objects.get(name=name)
                ingredient.quantity = new_quantity
                ingredient.save()
                return redirect('ingredient_success')
            except Ingredient.DoesNotExist:
                form.add_error('name', 'Ingredient does not exist.')
    else:
        form = UpdateIngredientForm()
    return render(request, 'update_ingredient.html', {'form': form})

def ingredient_success(request):
    return render(request, 'ingredient_success.html')