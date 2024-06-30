from django.urls import path
from django.contrib import admin
from . import views
from .views import signup,login, add_product, home, admin_view, inventory_view, add_ingredient, update_ingredient, ingredient_success


urlpatterns = [
    path('admin/', admin.site.urls),
    path('signup/', signup, name='signup'),
    path('login/', login, name='login'),
    path('addproduct/' ,add_product , name = 'addproduct' ),
    path('inventory/' ,inventory_view , name = 'addproduct' ),
    #path('update_inventory/' , update_inventory, name = 'inventory_update'),
    path('home/', home, name='home'),
    #path('cart/', cart_view, name='cart'),
    #path('add_to_cart/', add_to_cart, name='add_to_cart'),
    path('admin_page/', admin_view, name='admin_page'),
    path('add_ingredient/', add_ingredient, name='add_ingredient'),
    path('update-ingredient/', update_ingredient, name='update_ingredient'),
    path('ingredient-success/', ingredient_success, name='ingredient_success'),
]
