from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from .forms import ProductForm
from .forms import SignUpForm
from .forms import LoginForm
from .forms import IngredientForm
from .models import Product, Order
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.contrib.auth.decorators import login_required
from .forms import ProductForm, ProductIngredientFormSet
from .models import Product, Ingredient

def register(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            # Redirect to a success page or login page
            return redirect("login")
        # eror field
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

    return render(request, 'add_product.html', {'product_form': product_form, 'formset': formset})


def process_order(product_id, quantity_ordered):
    product = Product.objects.get(id=product_id)
    for product_ingredient in product.productingredient_set.all():
        ingredient = product_ingredient.ingredient
        ingredient.quantity -= product_ingredient.quantity * quantity_ordered
        ingredient.save()

def get_popular_products():
    return Order.objects.values('product__name').annotate(total_quantity=sum('quantity')).order_by('-total_quantity')

def cart_view(request):
    
    products = Product.objects.all()
    if request.method == 'POST':
        delivery_method = request.POST.get('delivery_method')
        product_ids = request.POST.getlist('products')
        selected_products = Product.objects.filter(id__in=product_ids)
        # tital price
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



def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    
    # Check if there are enough ingredients
    for pi in product.productingredient_set.all():
        if pi.ingredient.quantity < pi.quantity:
            raise ValidationError(f"Not enough {pi.ingredient.name} to fulfill the order for {product.name}")

    # If all ingredients are available, proceed with the order
    with transaction.atomic():
        for pi in product.productingredient_set.all():
            pi.ingredient.quantity -= pi.quantity
            pi.ingredient.save()

        # Create the order (Order model not shown, assuming you have one)
        order = Order.objects.create(product=product, user=request.user)

    return redirect('order_success')
