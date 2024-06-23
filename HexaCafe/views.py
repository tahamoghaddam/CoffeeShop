from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from .forms import ProductForm
from .forms import SignUpForm
from .forms import LoginForm
from .models import Product, Order
from django.http import HttpResponse


def register(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            # Redirect to a success page or login page
            return redirect("login")
    else:
        form = SignUpForm()
    return render(request, "user/register.html", {"form": form})



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
                    return redirect("home")
    else:
        form = LoginForm()
    return render(request, "registration/login.html", {"form": form})



def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('product_list')  
    else:
        form = ProductForm()
    return render(request, 'add_product.html', {'form': form})

def cart_view(request):
    
    products = Product.objects.all()
    if request.method == 'POST':
        delivery_method = request.POST.get('delivery_method')
        product_ids = request.POST.getlist('products')
        selected_products = Product.objects.filter(id__in=product_ids)
        total_price = sum(product.price for product in selected_products)
        order = Order.objects.create(delivery_method=delivery_method, total_price=total_price)
        order.products.set(selected_products)
        return HttpResponse("Order placed successfully!")
    
    return render(request, 'shop/cart.html', {'products': products})

def inventory_list(request):
    Ingredients = Ingredient.objects.all()
    return render(request, 'inventory_list.html', {'raw_materials': Ingredients})

def update_inventory(request, pk):
    Ingredient = get_object_or_404(Ingredient, pk=pk)
    if request.method == "POST":
        form = IngredientForm(request.POST, instance=Ingredient)
        if form.is_valid():
            form.save()
            return redirect('inventory_list')
    else:
        form = IngredientForm(instance=Ingredient)
    return render(request, 'update_inventory.html', {'form': form})