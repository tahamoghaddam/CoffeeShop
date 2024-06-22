from django.shortcuts import render
from .forms import SignUpForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from .forms import ProductForm


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
            return redirect('product_list')  # Redirect to a list of products or a success page
    else:
        form = ProductForm()
    return render(request, 'add_product.html', {'form': form})